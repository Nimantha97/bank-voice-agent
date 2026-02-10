import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import banking_router, chat_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bank ABC Voice Agent",
    description="AI-powered banking assistant with 6 customer service flows",
    version="1.1.0",
    docs_url="/docs",
)

# CORS Configuration - MUST be before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "bank-voice-agent",
            "version": "1.1.0"
        }
    )

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "service": "Bank ABC Voice Agent",
        "version": "1.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

# Include routers
app.include_router(banking_router)
app.include_router(chat_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
