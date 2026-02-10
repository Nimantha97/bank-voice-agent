"""
Voice AI Module - Isolated Implementation
Speech-to-Text (Groq Whisper) + Text-to-Speech (Groq TTS)
Zero coupling with existing chat endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
import os
import io
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["Voice AI"])

# Separate Groq client for voice (isolated from main agent)
def get_voice_client():
    """Get Groq client for voice APIs"""
    return OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

class TranscriptionResponse(BaseModel):
    """Speech-to-Text response"""
    text: str
    language: str = "en"

class SynthesisRequest(BaseModel):
    """Text-to-Speech request"""
    text: str
    voice: str = "autumn"

class VoiceChatRequest(BaseModel):
    """Voice chat request"""
    message: str
    customer_id: Optional[str] = None
    verified: bool = False
    session_id: Optional[str] = None

class VoiceChatResponse(BaseModel):
    """Voice chat response"""
    text_response: str
    audio_url: Optional[str] = None
    session_id: str
    requires_verification: bool = False
    flow: Optional[str] = None

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Speech-to-Text using Groq Whisper
    
    Upload audio file (WAV, MP3, M4A) and get transcribed text
    """
    try:
        audio_bytes = await audio.read()
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = audio.filename or "audio.wav"
        
        client = get_voice_client()
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=audio_file,
            language="en"
        )
        
        logger.info(f"Transcribed: {transcription.text[:50]}...")
        
        return TranscriptionResponse(
            text=transcription.text,
            language="en"
        )
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/synthesize")
async def synthesize_speech(text: str = Form(...), voice: str = Form("autumn")):
    """
    Text-to-Speech using Groq Orpheus
    
    Convert text to speech audio (WAV)
    """
    try:
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(text) > 4096:
            raise HTTPException(status_code=400, detail="Text too long (max 4096 chars)")
        
        client = get_voice_client()
        
        # Groq Orpheus requires specific voice format
        valid_voices = ["autumn", "diana", "hannah", "austin", "daniel", "troy"]
        selected_voice = voice if voice in valid_voices else "autumn"
        
        response = client.audio.speech.create(
            model="canopylabs/orpheus-v1-english",
            voice=selected_voice,
            input=text,
            response_format="wav"
        )
        
        logger.info(f"Synthesized: {text[:50]}...")
        
        return Response(
            content=response.content,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

@router.post("/chat", response_model=VoiceChatResponse)
async def voice_chat(request: VoiceChatRequest):
    """
    Voice-enabled chat
    
    Accepts text (from transcription) and returns text (for synthesis)
    Uses Pydantic AI agent for processing
    """
    try:
        from app.agent.pydantic_agent import process_with_pydantic_ai
        import uuid
        
        session_id = request.session_id or str(uuid.uuid4())
        
        result = await process_with_pydantic_ai(
            request.message,
            request.customer_id,
            request.verified,
            session_id
        )
        
        return VoiceChatResponse(
            text_response=result["response"],
            session_id=session_id,
            requires_verification=result.get("requires_verification", False),
            flow=result.get("flow")
        )
        
    except Exception as e:
        logger.error(f"Voice chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Voice chat failed: {str(e)}")

@router.get("/health")
def voice_health():
    """Voice AI health check"""
    return {
        "status": "healthy",
        "service": "voice-ai",
        "features": {
            "speech_to_text": "whisper-large-v3-turbo",
            "text_to_speech": "canopylabs/orpheus-v1-english",
            "voice_chat": "enabled"
        }
    }
