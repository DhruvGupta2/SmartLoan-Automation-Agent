🏦 SmartLoan Automation Agent


AI-powered Loan Processing System using Agentic Workflow (LangGraph + Gemini + Gradio)


SmartLoan Automation Agent is an end-to-end loan origination system built using an Agentic AI architecture.
It simulates a realistic loan journey — from customer interaction to verification, underwriting, credit checks, and automated sanction letter generation.


This project demonstrates how AI agents, mock financial APIs, and LLM-powered conversations can automate real-world banking workflows.


🚀 Features
1. Agentic Architecture (Master + Worker Agents)


Master Agent orchestrates the full loan process using LangGraph.


Worker Agents include:


Sales Agent → greets customer, collects name & loan amount


Verification Agent → verifies KYC + last 4 digits of phone


Underwriting Agent → evaluates credit score, salary, EMI limits


Sanction Letter Agent → generates PDF approval letter


2. Realistic Loan Decision Engine


Underwriting includes:


Fetch credit score from mock Credit Bureau API


Fetch salary & pre-approved limit from OfferMart API


Auto-approve if loan ≤ limit


If loan ≤ 2× limit → request salary slip, ensure EMI ≤ 50% salary


Reject if:


Loan > 2× limit


Credit score < 700


3. Synthetic Data (10+ Customers)


Each customer contains:


KYC details


Phone number


Pre-approved personal loan limit


Monthly salary


Credit score (out of 900)


Stored in customers.json.


4. Dual Interface


✔ CLI Version → Fully interactive terminal flow
✔ Gradio Web App → Chat-style UI with file upload & PDF download


5. Automated PDF Sanction Letter


Using FPDF, the system generates a professionally formatted sanction letter:


Customer name


Approved amount


Date


Approval reason


6. LLM Integration (Gemini)


Used for:


Customer-friendly responses


Short explanations of underwriting decisions


Sales-style guidance


🧱 Project Architecture
/project
│── agent.py                # LangGraph master orchestrator
│── gradio_app.py           # Gradio-based chat interface
│── tools.py                # Underwriting logic, PDF generation, helpers
│── crm_server.py           # Mock CRM API
│── offer_mart.py           # Mock OfferMart API
│── credit_bureau.py        # Mock Credit Bureau API
│── gemini_api.py           # Gemini API wrapper
│── customers.json          # Synthetic customer dataset
│── requirements.txt        
│── README.md               


🛠️ Technologies Used


Python


LangGraph (Agent orchestration)


Gradio (Chat UI)


Gemini API (LLM messaging)


FPDF (PDF generation)


JSON Mock APIs (CRM, OfferMart, Credit Bureau)


SQLite (LangGraph checkpointing)


Regex, Logging, Environment Variables


📌 How It Works (Flowchart)


Start Chat


Sales Agent gathers name + loan amount


Verification Agent validates KYC + mobile last 4 digits


Underwriting Agent retrieves:


Credit score


Salary


Pre-approved limit


Decision:


APPROVE (within limit)


PAYSALARY_REQUIRED (≤ 2× limit)


REJECT


If approved → Generate PDF Sanction Letter


📂 Running the Project
1. Install dependencies
pip install -r requirements.txt


2. Add your Gemini API Key


Create a .env file:


GEMINI_API_KEY=your_key_here


3. Run CLI Version
python agent.py


4. Run Gradio App
python gradio_app.py


After launch:


Enter your name


Enter loan amount


Provide last 4 digits of phone


Upload salary slip (if required)


Download sanction letter (if approved)


🧪 Sample Synthetic Customer (from customers.json)
{
  "full_name": "Rohan Verma",
  "kyc_details": {"mobile": "919890000009", "address": "Noida"},
  "financial_profile": {
    "credit_score": 760,
    "pre_approved_limit": 220000,
    "monthly_salary": 65000
  }
}


📄 Sanction Letter Example


Automatically generated PDF contains:


Customer Name


Approved Amount


Date


Approval Reason


📎 Key Highlights (Good for your Resume)


Implemented multi-agent workflow using LangGraph for loan automation.


Built mock financial APIs (CRM, OfferMart, Credit Bureau).


Developed a realistic underwriting engine with EMI & credit score rules.


Added Gradio chat UI, salary slip upload, and auto-generated sanction PDFs.


🤝 Contributions


Feel free to open issues, submit pull requests, or suggest improvements.


📜 License


This project is released under the MIT License.
