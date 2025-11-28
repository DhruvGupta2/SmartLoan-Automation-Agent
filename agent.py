# file: agent.py
"""
Simple, beginner-friendly Loan Automation orchestrator using LangGraph.
- Uses a dict as the state schema (avoids LangGraph schema warning).
- Uses SqliteSaver checkpointer correctly (requires configurable keys on invoke).
- Calls your existing tools.perform_underwriting and generate_sanction_letter.
- Adds an LLM explanation via gemini_api.call_gemini.
"""

import sqlite3
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

# local helpers (must exist in your tools.py and gemini_api.py)
from tools import verify_kyc, verify_phone, perform_underwriting, generate_sanction_letter, chat_with_customer
from gemini_api import call_gemini

# ----------------------------
# Checkpointer (SqliteSaver)
# ----------------------------
# create sqlite connection (allow multi-threading)
_conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
_checkpointer = SqliteSaver(_conn)  # your requested saver

# ----------------------------
# Initial state factory
# ----------------------------
def create_initial_state():
    """
    return a plain dict state. LangGraph accepts 'dict' as state schema, which
    removes the invalid-schema warning you saw earlier.
    """
    return {
        "customer_name": "",
        "loan_amount": 0.0,
        "kyc_verified": False,
        "underwriting_result": None,
        "sanction_file": None,
        "__next__": None,   # LangGraph flow helper (optional)
    }

# ----------------------------
# Worker Agents (simple and explicit)
# ----------------------------

def sales_agent(state: dict):
    print("\n💬 Sales Agent (Riya): Hello! I’m Riya from LoanMart. How can I help you today?")

    # Step 1: Ask user reason for loan (friendly chat)
    user_input = input("You: ").strip()

    # Step 2: Ask full name (if not already in state)
    if not state.get("customer_name"):
        print("💬 Sales Agent (Riya): Great! Could you please tell me your full name?")
        state["customer_name"] = input("You: ").strip()

    # Step 3: Ask loan amount
    if not state.get("loan_amount"):
        print(f"💬 Sales Agent (Riya): Thanks, {state['customer_name']}! How much would you like to borrow?")
        while True:
            val = input("You: ").strip()
            try:
                state["loan_amount"] = float(val.replace("₹", "").replace(",", ""))
                break
            except Exception:
                print("💬 Sales Agent: Please enter a valid numeric amount (e.g., 50000).")

  

    # Step 4: LLM friendly prompt summarizing conversation
    try:
        prompt = (
            f"User {state['customer_name']} said: '{user_input}'. "
            f"They want a loan of ₹{state['loan_amount']}. "
            "Respond as a friendly, convincing Sales Agent guiding them to proceed and make it breif."
        )
        reply = call_gemini(prompt)
        print(f"💬 Sales Agent (Riya): {reply}")
    except Exception as e:
        print(f"[LLM Error] {e}")

    # Proceed to verification
    state["__next__"] = "verify_kyc"
    return state


def verification_agent(state: dict):
    print("\n🧍 VERIFICATION AGENT:")
    
    # Step 1: Check if KYC exists
    kyc_result = verify_kyc(state["customer_name"])
    if not (isinstance(kyc_result, dict) and kyc_result.get("status") == "success"):
        print(" KYC record not found in CRM.")
        state["kyc_verified"] = False
        state["underwriting_result"] = {"decision": "REJECT", "reason": "KYC not found"}
        state["__next__"] = END
        return state
    
    # Step 2: Ask last 4 digits of phone for verification
    last4 = input("Enter last 4 digits of your mobile number for verification: ").strip()
    phone_result = verify_phone(state["customer_name"], last4)
    
    if phone_result.get("status") == "success":
        state["kyc_verified"] = True
        print("✅ KYC + Phone Verified!")
        state["__next__"] = "underwriting"
    else:
        state["kyc_verified"] = False
        state["underwriting_result"] = {"decision": "REJECT", "reason": phone_result.get("message", "Phone verification failed")}
        print(f"❌ Verification failed: {phone_result.get('message')}")
        state["__next__"] = END

    return state


def underwriting_agent(state: dict):
    print("\n💼 UNDERWRITING AGENT:")

    # safety: check KYC flag
    if not state.get("kyc_verified"):
        print("⚠️ Cannot proceed — KYC not verified.")
        state["underwriting_result"] = {"decision": "REJECT", "reason": "KYC not verified"}
        state["__next__"] = END
        return state

    result = perform_underwriting(state["customer_name"], state["loan_amount"])
    state["underwriting_result"] = result

    decision = result.get("decision")
    reason = result.get("reason", "")
    print(f"Decision: {decision} | Reason: {reason}")

    #  Show uploaded file if available
    if "uploaded_slip" in result:
        print(f"📎 Uploaded slip: {result['uploaded_slip']}")

    # Ask Gemini for friendly explanation
    try:
        prompt = (
            f"Customer {state['customer_name']} requested ₹{state['loan_amount']}. "
            f"Underwriting returned: {decision} because: {reason}. "
            "Please give one friendly sentence explanation for the customer."
        )
        explanation = call_gemini(prompt)
        print(f"🤖 LLM says: {explanation}")
        state["underwriting_result"]["llm_explanation"] = explanation
    except Exception as e:
        print(f"[LLM Error] {e}")

    # Move next
    if decision == "APPROVE" or decision == "APPROVED":
        state["__next__"] = "sanction_letter"
    else:
        state["__next__"] = END

    return state


def sanction_agent(state: dict):
    print("\n📄 SANCTION AGENT:")
    decision = (state.get("underwriting_result") or {}).get("decision")
    if decision == "APPROVE" or decision == "APPROVED":
        # generate_sanction_letter uses FPDF in your tools.py
        file_path = generate_sanction_letter(state["customer_name"], state["loan_amount"])
        state["sanction_file"] = file_path
        print(f" Sanction letter created: {file_path}")
    else:
        print(" Loan not approved — no sanction letter generated.")
    state["__next__"] = END
    return state

# ----------------------------
# Master Agent (orchestrator) with checkpointer config
# ----------------------------
def master_agent():
    print("🏦 Welcome to SmartLoan Automation System!")

    # Use dict as the state schema to avoid schema warnings
    workflow = StateGraph(dict)

    # register nodes (names are important for edges / checkpoint readability)
    workflow.add_node("sales", sales_agent)
    workflow.add_node("verify_kyc", verification_agent)
    workflow.add_node("underwriting", underwriting_agent)
    workflow.add_node("sanction_letter", sanction_agent)

    # simple linear edges (graph controls allowed transitions)
    workflow.set_entry_point("sales")
    workflow.add_edge("sales", "verify_kyc")
    workflow.add_edge("verify_kyc", "underwriting")
    workflow.add_edge("underwriting", "sanction_letter")  # only if APPROVE
    workflow.add_edge("underwriting", END)                # for REJECT
    workflow.add_edge("verify_kyc", END)
    workflow.add_edge("sanction_letter", END)

    # compile with checkpointer (SqliteSaver)
    graph = workflow.compile(checkpointer=_checkpointer)

    # create initial state
    state = create_initial_state()

    # get a thread id (required by LangGraph checkpointer)
    # we use customer_name as thread id (ask if empty). This makes the checkpoint keyed per user.
    if not state.get("customer_name"):
        name = input("Enter customer full name to start (this will be the checkpoint thread id): ").strip()
        state["customer_name"] = name

    thread_id = state["customer_name"] or "loan_default_thread"

    # LangGraph requires configurable keys like thread_id / checkpoint_ns / checkpoint_id
    config = {"configurable": {"thread_id": str(thread_id), "checkpoint_ns": "loan_agent_ns"}}

    # invoke graph with config so checkpointer knows where to store/load checkpoints
    # graph.invoke will persist state between nodes via checkpointer
    graph.invoke(state, config=config)

    print("\n🎉 Process completed. Thank you for using SmartLoan!")
    print("Final underwriting result:", state.get("underwriting_result"))
    if state.get("sanction_file"):
        print("Sanction file:", state["sanction_file"])

# ----------------------------
# CLI entrypoint
# ----------------------------
if __name__ == "__main__":
    master_agent()
