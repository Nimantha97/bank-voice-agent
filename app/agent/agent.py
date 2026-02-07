from openai import OpenAI
from typing import Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize LangFuse
try:
    from langfuse import Langfuse

    langfuse = Langfuse(
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        host=os.getenv("LANGFUSE_BASE_URL")
    )
    LANGFUSE_ENABLED = True
    print("✅ LangFuse initialized successfully")
except Exception as e:
    print(f"⚠️ LangFuse not available: {e}")
    LANGFUSE_ENABLED = False

# Lazy initialization of OpenAI client
_client = None

def get_client():
    """Get or create OpenAI client (lazy initialization)"""
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        _client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
    return _client

INTENT_SYSTEM_PROMPT = """You are a banking intent classifier. Analyze the user's message and classify it into ONE of these flows:

1. CARD_ATM_ISSUES
   - Lost, stolen, or damaged cards
   - ATM problems (cash not dispensed, card stuck, ATM errors)
   - Declined payments or transaction failures
   - Card activation or replacement
   - Examples: "lost my card", "ATM didn't give cash", "card declined", "reporting ATM issue"

2. ACCOUNT_SERVICING
   - Balance inquiries
   - Transaction history or statements
   - Profile updates (address, phone, email)
   - Account information requests
   - Examples: "check balance", "recent transactions", "update address", "account details"

3. ACCOUNT_OPENING
   - New account creation
   - Document requirements
   - Eligibility questions
   - Appointment scheduling
   - Examples: "open new account", "what documents needed", "am I eligible"

4. DIGITAL_SUPPORT
   - Login problems
   - OTP/verification code issues
   - App crashes or errors
   - Device registration
   - Password reset
   - Examples: "can't login", "OTP not received", "app not working", "forgot password"

5. TRANSFERS_PAYMENTS
   - Money transfers (domestic/international)
   - Bill payments
   - Beneficiary management
   - Failed or pending transfers
   - Examples: "transfer money", "pay bill", "add beneficiary", "transfer failed"

6. ACCOUNT_CLOSURE
   - Close account requests
   - Account termination
   - Reason for leaving
   - Examples: "close my account", "cancel account", "terminate account"

Respond with ONLY the flow name (e.g., "CARD_ATM_ISSUES"). No explanation."""


def classify_intent(user_message: str) -> str:
    """Classify user intent into one of 6 banking flows"""
    client = get_client()
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

    # Get customer cards for any card/ATM related query
    cards = get_customer_cards(customer_id)
    if not cards:
        return {"response": "No cards found for your account.", "flow": "CARD_ATM_ISSUES"}

    card_list = "\n".join(
        [f"- {c['card_type']} ({c['card_id']}) ending in {c['card_number'][-4:]} - Status: {c['status']}" for c in cards])
    
    # Check if user wants to block a specific card (with card_id)
    if any(word in user_message.lower() for word in ["block", "freeze"]):
        # Check if card_id is mentioned (e.g., "block CARD001")
        for card in cards:
            if card['card_id'].lower() in user_message.lower():
                if card['status'] == 'blocked':
                    return {
                        "response": f"Card {card['card_number']} is already blocked.",
                        "flow": "CARD_ATM_ISSUES"
                    }
                # Block the card
                reason = "Customer request - " + ("lost" if "lost" in user_message.lower() else "stolen" if "stolen" in user_message.lower() else "security")
                result = block_card(card['card_id'], reason)
                return {
                    "response": result,
                    "flow": "CARD_ATM_ISSUES",
                    "action": "card_blocked"
                }
        
        # If no specific card mentioned, show list
        return {
            "response": f"I can help block your card. Here are your cards:\n{card_list}\n\nPlease specify which card you'd like to block by saying the card ID (e.g., 'block CARD001').",
            "flow": "CARD_ATM_ISSUES",
            "action": "list_cards",
            "cards": cards
        }
    
    # Check for lost/stolen keywords
    if any(word in user_message.lower() for word in ["lost", "stolen"]):
        return {
            "response": f"I understand your card is {'lost' if 'lost' in user_message.lower() else 'stolen'}. Here are your cards:\n{card_list}\n\nWhich card would you like to block? Please provide the card ID (e.g., 'block CARD001').",
            "flow": "CARD_ATM_ISSUES",
            "action": "list_cards",
            "cards": cards
        }
    
    # For ATM issues or general card queries, show cards
    return {
        "response": f"I can help with that. Here are your cards:\n{card_list}\n\nWhich card is having the issue?",
        "flow": "CARD_ATM_ISSUES",
        "action": "list_cards",
        "cards": cards
    }


def handle_account_servicing(user_message: str, customer_id: Optional[str], verified: bool) -> Dict:
    """Handle account servicing requests"""
    from app.tools.banking import get_account_balance, get_recent_transactions

    if not verified:
        return {
            "response": "I can help with account servicing. First, I need to verify your identity. Please provide your Customer ID and PIN.",
            "requires_verification": True,
            "flow": "ACCOUNT_SERVICING"
        }

    # Check for balance query
    if any(word in user_message.lower() for word in ["balance", "how much", "money", "account"]):
        balance_info = get_account_balance(customer_id)
        return {
            "response": f"Your {balance_info['account_type']} account (#{balance_info['account_number']}) has a balance of ${balance_info['balance']:,.2f}",
            "flow": "ACCOUNT_SERVICING",
            "action": "balance_check"
        }

    # Check for transaction query
    if any(word in user_message.lower() for word in ["transaction", "statement", "history", "recent"]):
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

    # Default: show balance as most common query
    balance_info = get_account_balance(customer_id)
    return {
        "response": f"Your {balance_info['account_type']} account (#{balance_info['account_number']}) has a balance of ${balance_info['balance']:,.2f}. I can also help with transaction history or profile updates.",
        "flow": "ACCOUNT_SERVICING",
        "action": "balance_check"
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


def handle_help_and_faq(user_message: str) -> Optional[Dict]:
    """Handle common questions about the bot's capabilities"""
    message_lower = user_message.lower().strip()
    
    # Help/capability questions (exact matches or starts with)
    help_keywords = ["what can you do", "help me", "show features", "capabilities", 
                     "what do you do", "how can you help", "what are you", "who are you"]
    
    if any(keyword in message_lower for keyword in help_keywords) or message_lower == "help":
        return {
            "response": """I'm your Bank ABC AI Assistant! Here's what I can help you with:

🏦 **Account Services**
• Check account balance
• View recent transactions
• Update your address or profile

💳 **Card & ATM Issues**
• Report lost or stolen cards
• Block cards immediately
• Report ATM problems
• Handle declined payments

📱 **Digital Banking Support**
• Login issues
• OTP/verification problems
• App crashes or errors

💸 **Transfers & Payments**
• Money transfers
• Bill payments
• Beneficiary management

🆕 **Account Opening**
• New account inquiries
• Document requirements

❌ **Account Closure**
• Close account requests

Just tell me what you need! For security, I'll verify your identity before accessing account information.

**Examples:**
• "What's my balance?"
• "I lost my credit card"
• "Show my recent transactions""",
            "flow": "HELP",
            "action": "help_displayed"
        }
    
    # Greetings (exact matches only to avoid false positives)
    greeting_patterns = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
    # Check if message is ONLY a greeting (not part of another word)
    if message_lower in greeting_patterns or any(message_lower.startswith(g + " ") or message_lower.startswith(g + "!") for g in greeting_patterns):
        return {
            "response": "Hello! Welcome to Bank ABC. I'm your AI banking assistant. How can I help you today?\n\nYou can ask about your balance, report card issues, check transactions, or say 'help' to see all features.",
            "flow": "GREETING"
        }
    
    # Thanks (exact matches)
    thanks_patterns = ["thank you", "thanks", "thank you very much", "thanks a lot"]
    if any(message_lower == pattern or message_lower.startswith(pattern + " ") for pattern in thanks_patterns):
        return {
            "response": "You're welcome! Is there anything else I can help you with today?",
            "flow": "THANKS"
        }
    
    return None


def process_message(user_message: str, customer_id: Optional[str] = None, verified: bool = False) -> Dict:
    """Main agent processing function with LangFuse tracing"""
    
    # Check for help/FAQ first (before intent classification)
    help_response = handle_help_and_faq(user_message)
    if help_response:
        return help_response

    if LANGFUSE_ENABLED:
        try:
            # Use context manager for proper span lifecycle
            with langfuse.start_as_current_span(
                    name="banking-chat",
                    input={"message": user_message, "customer_id": customer_id, "verified": verified}
            ):
                # Classify intent
                intent = classify_intent(user_message)

                # Log intent classification with more details
                langfuse.create_event(
                    name="intent-classification",
                    input={"message": user_message, "verified": verified},
                    output={"intent": intent, "customer_id": customer_id}
                )

                # Route to appropriate handler
                if intent == "CARD_ATM_ISSUES":
                    result = handle_card_atm_issues(user_message, customer_id, verified)
                elif intent == "ACCOUNT_SERVICING":
                    result = handle_account_servicing(user_message, customer_id, verified)
                else:
                    result = handle_simple_flow(intent)

                # Update span with result and metadata
                langfuse.update_current_span(
                    output=result,
                    metadata={
                        "intent": intent,
                        "verified": verified,
                        "customer_id": customer_id,
                        "flow": result.get("flow"),
                        "action": result.get("action")
                    }
                )

                # Flush to send data
                langfuse.flush()

                return result

        except Exception as e:
            print(f"LangFuse error: {e}")
            # Fallback without tracing
            pass

    # Execute without LangFuse if disabled or error
    intent = classify_intent(user_message)

    if intent == "CARD_ATM_ISSUES":
        result = handle_card_atm_issues(user_message, customer_id, verified)
    elif intent == "ACCOUNT_SERVICING":
        result = handle_account_servicing(user_message, customer_id, verified)
    else:
        result = handle_simple_flow(intent)

    print(f"[TRACE] User: {customer_id or 'anonymous'} | Intent: {intent} | Flow: {result.get('flow')}")
    return result