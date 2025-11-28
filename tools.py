# file: tools.py
import os
from fpdf import FPDF
from datetime import datetime
from gemini_api import call_gemini
from crm_server import CRMServer
from credit_bureau import CreditBureau
from offer_mart import OfferMart

# Initialize mock APIs
crm = CRMServer()
bureau = CreditBureau()
offers = OfferMart()


def chat_with_customer(prompt, conversation_history):
    """
    Generates a friendly response from the sales agent using the LLM.
    """
    full_prompt = f"""
    You are a friendly and persuasive loan sales agent named Riya.
    You help customers apply for personal loans in a warm, natural tone.
    Guide them step-by-step to provide their name, loan amount, and mobile number.
    Keep conversation short, polite, and goal-oriented.

    Conversation so far:
    {conversation_history}

    Customer said: "{prompt}"
    """

    response = call_gemini(full_prompt)
    return response


def verify_kyc(name: str) -> dict:
    """Verify customer KYC from CRM."""
    return crm.get_kyc_details(name)

def verify_phone(name: str, last4_digits: str) -> dict:
    """Verify last 4 digits of phone number from CRM."""
    return crm.verify_phone_last4(name, last4_digits)

def fetch_credit_score(name: str) -> dict:
    """Fetch credit score from Credit Bureau."""
    return bureau.get_credit_score(name)

def get_offer_details(name: str) -> dict:
    """Fetch pre-approved limit & salary."""
    return offers.get_offer(name)

def perform_underwriting(name: str, loan_amount: float) -> dict:
    """
    Underwriting logic:
    1. Approve if loan <= pre-approved limit.
    2. If loan <= 2x limit, request salary slip and approve only if EMI <= 50% of salary.
    3. Reject if loan > 2x limit or credit score < 700.
    """
    offer = offers.get_offer(name)
    score_info = bureau.get_credit_score(name)

    if offer["status"] != "success" or score_info["status"] != "success":
        return {"decision": "REJECT", "reason": "Customer data missing"}

    limit = offer["limit"]
    salary = offer["salary"]
    score = score_info["score"]

    if score < 700:
        return {"decision": "REJECT", "reason": f"Low credit score: {score}"}

    # Within pre-approved limit → approve directly
    if loan_amount <= limit:
        return {"decision": "APPROVE", "reason": "Within pre-approved limit"}

    # Above limit but ≤ 2× limit → request salary slip
    elif loan_amount <= 2 * limit:
        print("Loan above pre-approved limit. Please upload your salary slip to continue.")

        # Keep asking until a "file path" is provided
        slip_path = ""
        while not slip_path:
            slip_path = input("Enter path to your salary slip file: ").strip()
            if not slip_path:
                print(" No file provided. Please upload your salary slip to continue.")

        # Simulate checking the slip (in real app, we would validate PDF/Excel)
        print(f"✅ Salary slip received: {slip_path}")

        # EMI calculation (2 years, 14% flat interest)
        total_repayment = loan_amount + loan_amount * 0.14 * 2
        emi = total_repayment / 24
        if emi <= 0.5 * salary:
            return {"decision": "APPROVE", "reason": f"EMI ₹{emi:,.2f} within 50% salary"}
        else:
            return {"decision": "REJECT", "reason": f"EMI ₹{emi:,.2f} exceeds 50% salary"}

    else:
        return {"decision": "REJECT", "reason": "Loan exceeds 2× pre-approved limit"}

def generate_sanction_letter(name: str, amount: float) -> str:
    """Generate a simple sanction letter PDF."""
    file_name = f"Sanction_Letter_{name.replace(' ', '_')}.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Loan Sanction Letter", ln=True, align="C")
    pdf.cell(200, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.cell(200, 10, f"Customer: {name}", ln=True)
    pdf.cell(200, 10, f"Approved Amount: INR{amount:,.2f}", ln=True)
    pdf.multi_cell(0, 10, "Your loan application has been approved based on your credit and income profile.")
    pdf.output(file_name)
    print(f"[PDF] Created {file_name}")
    return file_name

def upload_salary_slip() -> str:
    """
    Simulates uploading a salary slip file.
    - For CLI: asks for a file path and checks existence.
    - Returns file path if valid, else None.
    """
    print("📤 Please upload your salary slip file (PDF or image).")
    while True:
        file_path = input("Enter the path to your salary slip file: ").strip()
        if os.path.exists(file_path):
            print(f"✅ Salary slip uploaded successfully: {file_path}")
            return file_path
        else:
            print(" File not found. Please try again.")

# Inside tools.py
def perform_final_underwriting_with_salary(loan_amount, salary):
    """
    Approves the loan if estimated EMI ≤ 50% of monthly salary.
    EMI is roughly estimated as 0.02 * loan_amount (2% of loan as monthly EMI)
    """
    emi = 0.02 * loan_amount
    if emi <= 0.5 * salary:
        return {
            "loan_status": "APPROVED",
            "emi": emi,
            "reason": f"EMI ₹{emi:.2f} ≤ 50% of salary ₹{salary:.2f}"
        }
    else:
        return {
            "loan_status": "REJECTED",
            "emi": emi,
            "reason": f"EMI ₹{emi:.2f} exceeds 50% of salary ₹{salary:.2f}"
        }
    
    
def process_uploaded_salary_slip(uploaded_file):
    """
    Handles salary slip uploaded via Gradio.
    `uploaded_file` is either:
      - a string path, or
      - a Gradio file object with `.name` or `.tmp_path`.
    """
    import os, shutil

    # Check if it's a Gradio file object
    if isinstance(uploaded_file, dict) and "name" in uploaded_file and "tmp_path" in uploaded_file:
        src_path = uploaded_file["tmp_path"]
        dest_path = f"./uploads/{uploaded_file['name']}"
        os.makedirs("./uploads", exist_ok=True)
        shutil.copy(src_path, dest_path)
        uploaded_file_path = dest_path
    else:
        uploaded_file_path = uploaded_file  # assume normal path

    # Dummy: extract monthly_salary (replace with real parsing)
    monthly_salary = 50000  # mock value

    return {
        "status": "success",
        "file_name": uploaded_file_path,
        "salary_info": {"monthly_salary": monthly_salary}
    }


# tools.py (add this function for Gradio)
def perform_underwriting_gradio(name: str, loan_amount: float) -> dict:
    """
    Gradio-friendly underwriting:
    - Approve if loan <= pre-approved limit.
    - If loan <= 2x limit, request salary slip (PAYSALARY_REQUIRED).
    - Reject if loan > 2x limit or credit score < 700.
    """
    offer = offers.get_offer(name)
    score_info = bureau.get_credit_score(name)

    if offer["status"] != "success" or score_info["status"] != "success":
        return {"decision": "REJECT", "reason": "Customer data missing"}

    limit = offer["limit"]
    salary = offer["salary"]
    score = score_info["score"]

    if score < 700:
        return {"decision": "REJECT", "reason": f"Low credit score: {score}"}

    # Within pre-approved limit → approve directly
    if loan_amount <= limit:
        return {"decision": "APPROVE", "reason": "Within pre-approved limit"}

    # Above limit but ≤ 2× limit → request salary slip
    elif loan_amount <= 2 * limit:
        # Return special decision to trigger payslip upload in Gradio
        return {
            "decision": "PAYSALARY_REQUIRED",
            "reason": "Loan above pre-approved limit. Requires salary slip."
        }

    # Above 2× limit → reject
    else:
        return {"decision": "REJECT", "reason": "Loan exceeds 2× pre-approved limit"}
