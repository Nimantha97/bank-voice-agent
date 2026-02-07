import json
import os
from typing import List, Dict, Optional
from datetime import datetime

# Path to data files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.json")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")

# Audit log
AUDIT_LOG = []

def load_customers() -> Dict:
    """Load customer data from JSON file"""
    with open(CUSTOMERS_FILE, 'r') as f:
        return json.load(f)

def load_transactions() -> Dict:
    """Load transaction data from JSON file"""
    with open(TRANSACTIONS_FILE, 'r') as f:
        return json.load(f)

def save_customers(data: Dict):
    """Save customer data to JSON file"""
    with open(CUSTOMERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def log_action(action: str, customer_id: str, details: Dict):
    """Log all banking actions for audit trail"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "customer_id": customer_id,
        "details": details
    }
    AUDIT_LOG.append(log_entry)
    print(f"[AUDIT] {action} - Customer: {customer_id}")

def verify_identity(customer_id: str, pin: str) -> Optional[Dict]:
    """
    CRITICAL: Verify customer identity before any sensitive operation
    Returns customer object if credentials are valid, None otherwise
    """
    try:
        data = load_customers()
        for customer in data["customers"]:
            if customer["customer_id"] == customer_id and customer["pin"] == pin:
                log_action("IDENTITY_VERIFIED", customer_id, {"success": True})
                return customer
        
        log_action("IDENTITY_VERIFICATION_FAILED", customer_id, {"success": False})
        return None
    except Exception as e:
        print(f"Error verifying identity: {e}")
        return None

def get_account_balance(customer_id: str) -> Optional[Dict]:
    """
    Get account balance for verified customer
    Returns account details or None if customer not found
    """
    try:
        data = load_customers()
        for customer in data["customers"]:
            if customer["customer_id"] == customer_id:
                result = {
                    "customer_id": customer_id,
                    "account_number": customer["account_number"],
                    "balance": customer["account_balance"],
                    "account_type": customer["account_type"]
                }
                log_action("BALANCE_CHECK", customer_id, result)
                return result
        return None
    except Exception as e:
        print(f"Error getting balance: {e}")
        return None

def get_recent_transactions(customer_id: str, count: int = 5) -> List[Dict]:
    """
    Get recent transactions for verified customer
    Returns list of transactions
    """
    try:
        data = load_transactions()
        transactions = data["transactions"].get(customer_id, [])
        recent = transactions[:count]
        log_action("TRANSACTIONS_RETRIEVED", customer_id, {"count": len(recent)})
        return recent
    except Exception as e:
        print(f"Error getting transactions: {e}")
        return []

def block_card(card_id: str, reason: str) -> str:
    """
    IRREVERSIBLE ACTION: Block a card
    Returns confirmation message
    
    Note: This function requires customer_id to be derived from card_id
    In production, card_id would be globally unique
    """
    try:
        data = load_customers()
        for customer in data["customers"]:
            for card in customer["cards"]:
                if card["card_id"] == card_id:
                    card["status"] = "blocked"
                    save_customers(data)
                    log_action("CARD_BLOCKED", customer["customer_id"], {
                        "card_id": card_id,
                        "reason": reason,
                        "card_number": card["card_number"]
                    })
                    return f"Card {card['card_number']} has been blocked successfully. Reason: {reason}"
        
        return "Card not found"
    except Exception as e:
        print(f"Error blocking card: {e}")
        return f"Error blocking card: {str(e)}"

def get_customer_cards(customer_id: str) -> List[Dict]:
    """Get all cards for a customer"""
    try:
        data = load_customers()
        for customer in data["customers"]:
            if customer["customer_id"] == customer_id:
                return customer["cards"]
        return []
    except Exception as e:
        print(f"Error getting cards: {e}")
        return []

def update_customer_address(customer_id: str, new_address: str) -> str:
    """Update customer address"""
    try:
        data = load_customers()
        for customer in data["customers"]:
            if customer["customer_id"] == customer_id:
                old_address = customer["address"]
                customer["address"] = new_address
                save_customers(data)
                log_action("ADDRESS_UPDATED", customer_id, {
                    "old_address": old_address,
                    "new_address": new_address
                })
                return f"Address updated successfully to: {new_address}"
        return "Customer not found"
    except Exception as e:
        print(f"Error updating address: {e}")
        return f"Error updating address: {str(e)}"

def get_audit_log() -> List[Dict]:
    """Get audit log for monitoring"""
    return AUDIT_LOG
