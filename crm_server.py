import json

def load_customers():
    with open("customers.json", "r") as f:
        return json.load(f)

class CRMServer:
    """Simulated CRM server that stores customer KYC details."""

    def __init__(self):
        self.customers = load_customers()

    def get_kyc_details(self, name: str) -> dict:
        print(f"[CRM] Looking up KYC for {name}...")
        for c in self.customers:
            if c["full_name"].lower() == name.lower():
                print("[CRM] KYC found.")
                return {"status": "success", "kyc": c["kyc_details"]}
        print("[CRM] KYC not found.")
        return {"status": "error", "message": "Customer not found"}

    def verify_phone_last4(self, name: str, last4_digits: str) -> dict:
        """Verify if last 4 digits match customer's phone number."""
        for c in self.customers:
            if c["full_name"].lower() == name.lower():
                phone = c["kyc_details"]["phone_number"]
                if phone[-4:] == last4_digits:
                    return {"status": "success", "message": "Phone verification successful"}
                else:
                    return {"status": "error", "message": "Phone number mismatch"}
        return {"status": "error", "message": "Customer not found"}
