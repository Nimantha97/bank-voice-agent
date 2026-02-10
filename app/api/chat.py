from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import Optional
from app.agent import process_message
from app.tools.banking import verify_identity
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat Agent"])

class ChatRequest(BaseModel):
    message: str
    customer_id: Optional[str] = None
    pin: Optional[str] = None
    session_id: Optional[str] = None
    verified: bool = False
    
    @validator('message')
    def message_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        if len(v) > 1000:
            raise ValueError('Message too long (max 1000 characters)')
        return v.strip()

class ChatResponse(BaseModel):
    response: str
    session_id: str
    requires_verification: bool = False
    flow: Optional[str] = None
    error: Optional[str] = None

# Session storage
sessions = {}

@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Main chat endpoint with AI agent"""
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        # Initialize session
        if session_id not in sessions:
            sessions[session_id] = {"verified": False, "customer_id": None}
        
        # Update session from frontend if verified
        if request.verified and request.customer_id:
            sessions[session_id]["verified"] = True
            sessions[session_id]["customer_id"] = request.customer_id
        
        # Handle verification with PIN
        if request.customer_id and request.pin:
            customer = verify_identity(request.customer_id, request.pin)
            if customer:
                sessions[session_id]["verified"] = True
                sessions[session_id]["customer_id"] = request.customer_id
                return ChatResponse(
                    response=f"Identity verified successfully, {customer['name']}. How can I help you today?",
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
    
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        return ChatResponse(
            response="I apologize, but I'm experiencing technical difficulties. Please try again in a moment.",
            session_id=session_id if 'session_id' in locals() else str(uuid.uuid4()),
            error="internal_error"
        )
