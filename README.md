# 🏦 SmartLoan Automation Agent
**AI-powered Loan Processing System using Agentic Workflow (LangGraph + Gemini + Gradio)**

SmartLoan Automation Agent is an end-to-end **loan origination system** built using an **Agentic AI architecture**.  
It simulates a realistic loan journey — from customer interaction to verification, underwriting, credit checks, all the way to automated sanction letter generation.

This project demonstrates how **AI agents**, **mock financial APIs**, and **LLM-powered conversations** can automate real-world banking workflows.

---

## 🚀 Features

### **1. Agentic Architecture (Master + Worker Agents)**
- **Master Agent** orchestrates the entire loan process using **LangGraph**.
- **Worker Agents**:
  - **Sales Agent** – collects name & loan amount
  - **Verification Agent** – verifies KYC + last 4 digits of phone (from CRM server)
  - **Underwriting Agent** – checks credit score, salary & EMI rules
  - **Sanction Letter Agent** – generates PDF sanction letter using FPDF

---

### **2. Realistic Loan Decision Engine**
Underwriting performs real-world checks:
- Fetches credit score (mock **Credit Bureau API**)
- Fetches salary + pre-approved limit (mock **OfferMart API**)
- **Auto-approve** if loan ≤ pre-approved limit  
- **Ask for salary slip** if loan ≤ 2× limit and verify EMI ≤ 50% of salary  
- **Reject** if:
  - Loan > 2× limit  
  - Credit score < 700  

---

### **3. Synthetic Customer Data**
A dataset of **10+ synthetic customers** stored in `customers.json`, each with:
- KYC details  
- Phone number  
- Salary  
- Credit score (out of 900)  
- Pre-approved loan limit  

---

### **4. Dual Interface**
✔ **CLI Version** — Fully interactive console flow  
✔ **Gradio Web App** — Chat-style interface with file upload & PDF download  

---

### **5. Automated PDF Sanction Letter**
The system generates a formal PDF containing:
- Customer name  
- Approved amount  
- Date  
- Approval reason  

---

### **6. LLM Integration (Gemini API)**
Used for:
- Friendly customer messages  
- Natural-language explanations  
- Sales guidance  

---

## 🧱 Project Architecture

/project
│── agent.py # LangGraph master orchestrator
│── gradio_app.py # Gradio-based chat interface
│── tools.py # Underwriting logic, PDF generation, helpers
│── crm_server.py # Mock CRM API
│── offer_mart.py # Mock OfferMart API
│── credit_bureau.py # Mock Credit Bureau API
│── gemini_api.py # Gemini API wrapper
│── customers.json # Synthetic customer dataset
│── requirements.txt
│── README.md



---

## 🛠️ Technologies Used

- **Python**
- **LangGraph** (Master–Worker Agent Orchestration)
- **Gradio** (Chat UI)
- **Gemini API** (LLM responses)
- **FPDF** (PDF generation)
- **JSON Mock APIs** (CRM, OfferMart, Credit Bureau)
- **SQLite** (Checkpointing for LangGraph)
- **Regex**, **Logging**, **Environment Variables**
- **Git / GitHub**

---

## 📌 Flow of the System

1. User starts conversation  
2. Sales Agent collects **name & loan amount**  
3. Verification Agent checks **KYC + last 4 digits of phone**  
4. Underwriting Agent retrieves:  
   - Credit score  
   - Monthly salary  
   - Pre-approved limit  
5. Decision outcomes:
   - **APPROVE** → within limit  
   - **PAYSALARY_REQUIRED** → within 2× limit  
   - **REJECT** → low credit score or > 2× limit  
6. If approved → **Generate PDF sanction letter**  

---

## 📂 How to Run

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
2. Add Gemini API Key
Create .env:

ini

GEMINI_API_KEY=your_key_here
3. Run the CLI Version
bash
Copy code
python agent.py
4. Run the Gradio Web App
bash
Copy code
python gradio_app.py
After Launch
Enter your name

Enter loan amount

Provide last 4 digits of phone

Upload salary slip (if required)

Download sanction letter when approved

🧪 Example Customer (from customers.json)

{
  "full_name": "Rohan Verma",
  "kyc_details": {"mobile": "919890000009", "address": "Noida"},
  "financial_profile": {
    "credit_score": 760,
    "pre_approved_limit": 220000,
    "monthly_salary": 65000
  }
}
📄 Sanction Letter
Auto-generated PDF includes:

Customer Name

Approved Amount

Date

Loan Approval Message

⭐ Key Highlights
Built multi-agent loan automation using LangGraph

Implemented realistic underwriting rules (limit, credit score, EMI checks)

Created mock CRM, OfferMart, and Credit Bureau APIs

Added Gradio front-end, file uploads, and PDF generation

🤝 Contributions
Issues and PRs are welcome!

📜 License
This project is released under the MIT License.









