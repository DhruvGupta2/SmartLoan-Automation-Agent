# file: offer_mart.py
import json

def load_customers():
    with open("customers.json", "r") as f:
        return json.load(f)

class OfferMart:
    """Mock Offer Mart providing pre-approved limits."""

    def __init__(self):
        self.customers = load_customers()

    def get_offer(self, name: str) -> dict:
        print(f"[OfferMart] Fetching pre-approved offer for {name}...")
        for c in self.customers:
            if c["full_name"].lower() == name.lower():
                profile = c["financial_profile"]
                return {
                    "status": "success",
                    "limit": profile["pre_approved_limit"],
                    "salary": profile["monthly_salary"]
                }
        print("[OfferMart] No offer found.")
        return {"status": "error", "message": "Customer not found"}
