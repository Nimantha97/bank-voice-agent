from openai import OpenAI
from typing import Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

INTENT_SYSTEM_PROMPT = """You are a banking intent classifier. Classify user queries into ONE of these flows:

1. CARD_ATM_ISSUES - Lost/stolen card, ATM problems, declined payments
2. ACCOUNT_SERVICING - Statements, profile updates, address changes
3. ACCOUNT_OPENING - New account, documents, eligibility
4. DIGITAL_SUPPORT - Login issues, OTP problems, app crashes
5. TRANSFERS_PAYMENTS - Failed transfers, bill payments
6. ACCOUNT_CLOSURE - Close account, retention

Respond with ONLY the flow name (e.g., "CARD_ATM_ISSUES")."""

def classify_intent(user_message: str) -> str:
    """Classify user intent into one of 6 banking flows"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": INTENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.1,
        max_tokens=50
    )
    return response.choices[0].message.content.strip()

def handle_card_atm_issues(user_message: str, customer_id: Optional[str], verified: bool) -> Dict:
    """Handle card and ATM related issues"""
    from app.tools.banking import get_customer_cards, block_card
    
    if not verified:
        return {
            "response": "I can help with card issues. First, I need to verify your identity. Please provide your Customer ID and PIN.",
            "requires_verification": True,
            "flow": "CARD_ATM_ISSUES"
        }
    
    # Check if user wants to block card
    if any(word in user_message.lower() for word in ["lost", "stolen", "block", "freeze"]):
        cards = get_customer_cards(customer_id)
        if not cards:
            return {"response": "No cards found for your account.", "flow": "CARD_ATM_ISSUES"}
        
        card_list = "\n".join([f"- {c['card_type']} ending in {c['card_number'][-4:]} (Status: {c['status']})" for c in cards])
        return {
            "response": f"I can help block your card. Here are your cards:\n{card_list}\n\nWhich card would you like to block?",
            "flow": "CARD_ATM_ISSUES",
            "action": "list_cards",
            "cards": cards
        }
    
    return {
        "response": "I can help with card issues like blocking cards, reporting ATM problems, or declined payments. What specific issue are you facing?",
        "flow": "CARD_ATM_ISSUES"
    }

def handle_account_servicing(user_message: str, customer_id: Optional[str], verified: bool) -> Dict:
    """Handle account servicing requests"""
    from app.tools.banking import get_account_balance, get_recent_transactions, update_customer_address
    
    if not verified:
        return {
            "response": "I can help with account servicing. First, I need to verify your identity. Please provide your Customer ID and PIN.",
            "requires_verification": True,
            "flow": "ACCOUNT_SERVICING"
        }
    
    # Check for balance inquiry
    if any(word in user_message.lower() for word in ["balance", "how much"]):
        balance_info = get_account_balance(customer_id)
        return {
            "response": f"Your {balance_info['account_type']} account (#{balance_info['account_number']}) has a balance of ${balance_info['balance']:,.2f}",
            "flow": "ACCOUNT_SERVICING",
            "action": "balance_check"
        }
    
    # Check for transaction history
    if any(word in user_message.lower() for word in ["transaction", "statement", "history"]):
        transactions = get_recent_transactions(customer_id, 5)
        txn_list = "\n".join([f"- {t['date']}: {t['description']} (${t['amount']})" for t in transactions])
        return {
            "response": f"Here are your recent transactions:\n{txn_list}",
            "flow": "ACCOUNT_SERVICING",
            "action": "transaction_history"
        }
    
    # Check for address update
    if any(word in user_message.lower() for word in ["address", "update", "change"]):
        return {
            "response": "I can help update your address. Please provide your new address.",
            "flow": "ACCOUNT_SERVICING",
            "action": "address_update_prompt"
        }
    
    return {
        "response": "I can help with balance checks, transaction history, or profile updates. What would you like to do?",
        "flow": "ACCOUNT_SERVICING"
    }

def handle_simple_flow(flow_name: str) -> Dict:
    """Handle simple routing for flows 3-6"""
    responses = {
        "ACCOUNT_OPENING": "I can help you open a new account. You'll need to provide documents and verify eligibility. Would you like to schedule an appointment?",
        "DIGITAL_SUPPORT": "I can help with digital banking issues like login problems, OTP issues, or app crashes. What specific problem are you experiencing?",
        "TRANSFERS_PAYMENTS": "I can help with transfers and bill payments. Are you having issues with a pending transfer or need to add a beneficiary?",
        "ACCOUNT_CLOSURE": "I understand you want to close your account. Before we proceed, may I ask why you're considering this? We might be able to help resolve any concerns."
    }
    return {
        "response": responses.get(flow_name, "I can help you with that. Please provide more details."),
        "flow": flow_name
    }

def process_message(user_message: str, customer_id: Optional[str] = None, verified: bool = False) -> Dict:
    """Main agent processing function"""
    
    # Classify intent
    intent = classify_intent(user_message)
    
    # Route to appropriate handler
    if intent == "CARD_ATM_ISSUES":
        return handle_card_atm_issues(user_message, customer_id, verified)
    elif intent == "ACCOUNT_SERVICING":
        return handle_account_servicing(user_message, customer_id, verified)
    else:
        return handle_simple_flow(intent)
