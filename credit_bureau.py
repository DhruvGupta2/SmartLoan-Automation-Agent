# file: credit_bureau.py
import json

def load_customers():
    with open("customers.json", "r") as f:
        return json.load(f)

class CreditBureau:
    """Mock credit bureau for returning a customer’s credit score."""

    def __init__(self):
        self.customers = load_customers()

    def get_credit_score(self, name: str) -> dict:
        print(f"[Credit Bureau] Checking credit score for {name}...")
        for c in self.customers:
            if c["full_name"].lower() == name.lower():
                score = c["financial_profile"]["credit_score"]
                return {"status": "success", "score": score}
        print("[Credit Bureau] Customer not found.")
        return {"status": "error", "message": "Customer not found"}
