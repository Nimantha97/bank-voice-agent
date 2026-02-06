from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.agent import process_message
from app.tools.banking import verify_identity
import uuid

router = APIRouter(prefix="/api/chat", tags=["Chat Agent"])

class ChatRequest(BaseModel):
    message: str
    customer_id: Optional[str] = None
    pin: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    requires_verification: bool = False
    flow: Optional[str] = None

# Session storage
sessions = {}

@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Main chat endpoint with AI agent"""
    session_id = request.session_id or str(uuid.uuid4())
    
    # Initialize session
    if session_id not in sessions:
        sessions[session_id] = {"verified": False, "customer_id": None}
    
    # Handle verification
    if request.customer_id and request.pin:
        if verify_identity(request.customer_id, request.pin):
            sessions[session_id]["verified"] = True
            sessions[session_id]["customer_id"] = request.customer_id
            return ChatResponse(
                response="Identity verified successfully. How can I help you today?",
                session_id=session_id,
                requires_verification=False
            )
        else:
            return ChatResponse(
                response="Invalid credentials. Please try again.",
                session_id=session_id,
                requires_verification=True
            )
    
    # Process message with agent
    result = process_message(
        request.message,
        sessions[session_id].get("customer_id"),
        sessions[session_id].get("verified", False)
    )
    
    return ChatResponse(
        response=result["response"],
        session_id=session_id,
        requires_verification=result.get("requires_verification", False),
        flow=result.get("flow")
    )
