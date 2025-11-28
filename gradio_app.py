# gradio_app.py
import gradio as gr
import re
from tools import (
    verify_kyc,
    verify_phone,
    perform_underwriting_gradio as perform_underwriting,
    generate_sanction_letter,
    process_uploaded_salary_slip,
    perform_final_underwriting_with_salary
)
from gemini_api import call_gemini

# --- State Management ---
def create_initial_state():
    return {
        "step": "start",
        "customer_name": "",
        "loan_amount": 0.0,
        "kyc_verified": False,
        "underwriting_result": None,
        "sanction_file": None,
        "payslip_file": None,
        "monthly_salary": None,
    }

# --- Main Chat Function ---
def chat_interface(message, history, state, uploaded_file):
    if state is None:
        state = create_initial_state()
    if history is None:
        history = []

    if message:
        history.append((message, None))

    step = state.get("step")

    # Step 1: Welcome
    if step == "start":
        bot_message = "Hello! I’m Riya from LoanMart. To begin, could you please tell me your full name?"
        state["step"] = "get_name"
        history.append((None, bot_message))
        return history, state, gr.update(value=None), gr.update(visible=False), None

    # Step 2: Get Name
    elif step == "get_name":
        clean_name = message.lower()
        for phrase in ["my name is", "i am", "it's"]:
            clean_name = clean_name.replace(phrase, "")
        state["customer_name"] = clean_name.strip().title()
        bot_message = f"Thanks, {state['customer_name']}! How much would you like to borrow?"
        state["step"] = "get_amount"
        history.append((None, bot_message))
        return history, state, gr.update(value=None), gr.update(visible=False), None

    # Step 3: Get Loan Amount
    elif step == "get_amount":
        try:
            amount_str = re.sub(r'[^\d.]', '', message)
            state["loan_amount"] = float(amount_str)
            prompt = (
                f"User {state['customer_name']} wants a loan of ₹{state['loan_amount']}. "
                "Respond as a friendly Sales Agent guiding them to the verification step. Make it brief."
            )
            llm_reply = call_gemini(prompt)
            bot_message = (
                f"{llm_reply}\n\n"
                "To proceed, I need to verify your identity. "
                "Please enter the **last 4 digits** of your registered mobile number."
            )
            state["step"] = "verify_phone_digits"
            history.append((None, bot_message))
        except:
            bot_message = "Invalid amount. Please enter a numeric value (e.g., 50000)."
            history.append((None, bot_message))
        return history, state, gr.update(value=None), gr.update(visible=False), None

    # Step 4: Verify Phone & Run Underwriting
    elif step == "verify_phone_digits":
        last4 = message.strip()
        kyc_result = verify_kyc(state["customer_name"])
        if kyc_result.get("status") != "success":
            bot_message = "❌ KYC not found."
            state["step"] = "done"
            history.append((None, bot_message))
            return history, state, gr.update(value=None), gr.update(visible=False), None

        phone_result = verify_phone(state["customer_name"], last4)
        if phone_result.get("status") != "success":
            bot_message = f"❌ Phone verification failed: {phone_result.get('message','')}"
            state["step"] = "done"
            history.append((None, bot_message))
            return history, state, gr.update(value=None), gr.update(visible=False), None

        history.append((None, "✅ KYC and Phone Verified! Running underwriting..."))

        # Run underwriting
        underwriting_result = perform_underwriting(state["customer_name"], state["loan_amount"])
        state["underwriting_result"] = underwriting_result
        decision = underwriting_result.get("decision", "REJECT").upper()

        if decision == "PAYSALARY_REQUIRED":
            state["step"] = "upload_payslip"
            bot_message = "💼 Loan above pre-approved limit. Please upload your salary slip to continue."
            history.append((None, bot_message))
            # Show file upload box
            return history, state, gr.update(value=None), gr.update(visible=True), None

        # Approved or rejected
        prompt = f"Customer {state['customer_name']}'s loan for ₹{state['loan_amount']} was {decision} because: {underwriting_result.get('reason','')}. Provide a friendly one-sentence explanation."
        llm_explanation = call_gemini(prompt)

        pdf_file = None
        if decision in ["APPROVE", "APPROVED"]:
            pdf_file = generate_sanction_letter(state["customer_name"], state["loan_amount"])
            state["sanction_file"] = pdf_file
            bot_message = f"🎉 Approved! {llm_explanation}\n📄 Sanction letter generated."
        else:
            bot_message = f"❌ Loan not approved. {llm_explanation}"

        state["step"] = "done"
        history.append((None, bot_message))
        return history, state, gr.update(value=None), gr.update(visible=False), pdf_file

    # Step 5: Upload Payslip for Final Underwriting
    elif step == "upload_payslip":
        if uploaded_file is None:
            bot_message = "💼 Please upload your salary slip to continue."
            history.append((None, bot_message))
            return history, state, gr.update(value=None), gr.update(visible=True), None

        # Process uploaded file
        payslip_result = process_uploaded_salary_slip(uploaded_file)
        if payslip_result["status"] != "success":
            bot_message = f"❌ Error uploading payslip: {payslip_result.get('message')}"
            history.append((None, bot_message))
            return history, state, gr.update(value=None), gr.update(visible=True), None

        state["payslip_file"] = payslip_result["file_name"]
        state["monthly_salary"] = payslip_result["salary_info"]["monthly_salary"]

        # Final underwriting
        loan_amount = state["loan_amount"]
        salary = state["monthly_salary"]
        final_result = perform_final_underwriting_with_salary(loan_amount, salary)
        state["underwriting_result"] = {
            "decision": final_result["loan_status"],
            "reason": final_result["reason"]
        }

        decision = final_result["loan_status"].upper()
        bot_message = f"💼 Underwriting Result: {decision} | {final_result['reason']}"
        pdf_file = None
        if decision in ["APPROVED", "APPROVE"]:
            pdf_file = generate_sanction_letter(state["customer_name"], state["loan_amount"])
            state["sanction_file"] = pdf_file
            bot_message += f"\n📄 Sanction letter generated."

        state["step"] = "done"
        history.append((None, bot_message))
        # Hide upload box after processing
        return history, state, gr.update(value=None), gr.update(visible=False), pdf_file

    # Done
    elif step == "done":
        bot_message = "✅ Loan process complete. Refresh to start a new application."
        history.append((None, bot_message))
        pdf_file = state.get("sanction_file")
        return history, state, gr.update(value=None), gr.update(visible=False), pdf_file

    return history, state, gr.update(value=None), gr.update(visible=False), None

# --- Gradio UI ---
with gr.Blocks(theme=gr.themes.Soft(), title="SmartLoan Agent") as demo:
    state = gr.State()
    gr.Markdown("## 🏦 SmartLoan Automation Chat Agent")
    chatbot = gr.Chatbot(label="Conversation", height=500)
    msg = gr.Textbox(label="Message", placeholder="Type your response...")
    payslip_upload = gr.File(label="Upload Salary Slip", file_types=[".pdf", ".xlsx", ".csv"], visible=False)
    pdf_download = gr.File(label="📄 Download Sanction Letter", interactive=False)

    # Load initial chat
    demo.load(
        fn=chat_interface,
        inputs=[msg, chatbot, state, payslip_upload],
        outputs=[chatbot, state, msg, payslip_upload, pdf_download]
    )

    # Submit messages
    msg.submit(
        fn=chat_interface,
        inputs=[msg, chatbot, state, payslip_upload],
        outputs=[chatbot, state, msg, payslip_upload, pdf_download]
    )
    payslip_upload.upload(
        fn=chat_interface,
        inputs=[msg, chatbot, state, payslip_upload],
        outputs=[chatbot, state, msg, payslip_upload, pdf_download]
    )

demo.launch()
