from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.tools.banking import (
    verify_identity,
    get_account_balance,
    get_recent_transactions,
    get_customer_cards,
    block_card,
    update_customer_address,
    get_audit_log
)

router = APIRouter(prefix="/api/banking", tags=["Banking Operations"])

class VerifyRequest(BaseModel):
    customer_id: str
    pin: str

class BalanceResponse(BaseModel):
    customer_id: str
    account_number: str
    balance: float
    account_type: str

class BlockCardRequest(BaseModel):
    card_id: str
    reason: str

class UpdateAddressRequest(BaseModel):
    new_address: str

@router.post("/verify")
def verify_customer(request: VerifyRequest):
    """Verify customer identity with ID and PIN"""
    customer = verify_identity(request.customer_id, request.pin)
    if customer:
        return {
            "verified": True,
            "customer": {
                "customer_id": customer["customer_id"],
                "name": customer["name"],
                "account_number": customer["account_number"],
                "balance": customer["account_balance"]
            }
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/balance/{customer_id}", response_model=BalanceResponse)
def get_balance(customer_id: str):
    """Get account balance for verified customer"""
    balance = get_account_balance(customer_id)
    if not balance:
        raise HTTPException(status_code=404, detail="Customer not found")
    return balance

@router.get("/transactions/{customer_id}")
def get_transactions(customer_id: str, count: int = 5):
    """Get recent transactions for customer"""
    transactions = get_recent_transactions(customer_id, count)
    return {"customer_id": customer_id, "transactions": transactions}

@router.get("/cards/{customer_id}")
def get_cards(customer_id: str):
    """Get all cards for customer"""
    cards = get_customer_cards(customer_id)
    if not cards:
        raise HTTPException(status_code=404, detail="No cards found")
    return {"customer_id": customer_id, "cards": cards}

@router.post("/block-card")
def block_customer_card(request: BlockCardRequest):
    """Block a card (irreversible action)"""
    result = block_card(request.card_id, request.reason)
    if "Error" in result or "not found" in result:
        raise HTTPException(status_code=400, detail=result)
    return {"success": True, "message": result}

@router.put("/address/{customer_id}")
def update_address(customer_id: str, request: UpdateAddressRequest):
    """Update customer address"""
    result = update_customer_address(customer_id, request.new_address)
    if "Error" in result or "not found" in result:
        raise HTTPException(status_code=400, detail=result)
    return {"success": True, "message": result}

@router.get("/audit-log")
def audit_log():
    """Get audit log for monitoring"""
    return {"audit_log": get_audit_log()}
