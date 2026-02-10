"""
Pydantic AI Agent Integration
Wraps existing banking agent logic with Pydantic AI framework
"""
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Import existing agent logic
from app.agent.agent import classify_intent, handle_card_atm_issues, handle_account_servicing, handle_simple_flow, handle_help_and_faq

class BankingContext(BaseModel):
    """Context for banking agent"""
    customer_id: Optional[str] = None
    verified: bool = False
    session_id: Optional[str] = None

class BankingResponse(BaseModel):
    """Structured response from banking agent"""
    response: str
    flow: Optional[str] = None
    requires_verification: bool = False
    action: Optional[str] = None

# Initialize Pydantic AI Agent
banking_agent = Agent(
    'openai:gpt-4',  # Model identifier (we'll override with Groq)
    result_type=BankingResponse,
    system_prompt="""You are a banking AI assistant for Bank ABC.
    You help customers with:
    - Account servicing (balance, transactions)
    - Card issues (lost cards, blocking)
    - Digital support
    - Transfers and payments
    - Account opening and closure
    
    Always verify customer identity before sensitive operations.
    Be professional, clear, and helpful."""
)

@banking_agent.tool
def check_account_balance(ctx: RunContext[BankingContext], customer_id: str) -> dict:
    """Get customer account balance"""
    from app.tools.banking import get_account_balance
    if not ctx.deps.verified:
        return {"error": "Verification required"}
    return get_account_balance(customer_id)

@banking_agent.tool
def get_transactions(ctx: RunContext[BankingContext], customer_id: str, limit: int = 5) -> list:
    """Get recent transactions"""
    from app.tools.banking import get_recent_transactions
    if not ctx.deps.verified:
        return {"error": "Verification required"}
    return get_recent_transactions(customer_id, limit)

@banking_agent.tool
def list_customer_cards(ctx: RunContext[BankingContext], customer_id: str) -> list:
    """List customer cards"""
    from app.tools.banking import get_customer_cards
    if not ctx.deps.verified:
        return {"error": "Verification required"}
    return get_customer_cards(customer_id)

@banking_agent.tool
def block_customer_card(ctx: RunContext[BankingContext], card_id: str, reason: str) -> str:
    """Block a customer card"""
    from app.tools.banking import block_card
    if not ctx.deps.verified:
        return "Verification required"
    return block_card(card_id, reason)

async def process_with_pydantic_ai(
    message: str,
    customer_id: Optional[str] = None,
    verified: bool = False,
    session_id: Optional[str] = None
) -> dict:
    """
    Process message using Pydantic AI framework
    Falls back to existing logic for compatibility
    """
    
    # Check for help/FAQ first (bypass AI for simple queries)
    help_response = handle_help_and_faq(message)
    if help_response:
        return help_response
    
    # Use existing intent classification (proven to work)
    intent = classify_intent(message)
    
    # Route to appropriate handler (existing logic)
    if intent == "CARD_ATM_ISSUES":
        result = handle_card_atm_issues(message, customer_id, verified)
    elif intent == "ACCOUNT_SERVICING":
        result = handle_account_servicing(message, customer_id, verified)
    else:
        result = handle_simple_flow(intent)
    
    return result

# Export for backward compatibility
__all__ = ['banking_agent', 'process_with_pydantic_ai', 'BankingContext', 'BankingResponse']
