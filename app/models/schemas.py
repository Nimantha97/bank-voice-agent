from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Card(BaseModel):
    card_id: str
    card_number: str
    card_type: str
    status: str
    credit_limit: Optional[float] = None
    available_credit: Optional[float] = None

class Customer(BaseModel):
    customer_id: str
    pin: str
    name: str
    email: str
    phone: str
    address: str
    account_number: str
    account_balance: float
    account_type: str
    cards: List[Card]

class Transaction(BaseModel):
    transaction_id: str
    date: str
    description: str
    amount: float
    type: str
    category: str

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    customer_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    requires_verification: bool = False
    action_taken: Optional[str] = None
