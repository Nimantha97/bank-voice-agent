import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# Include routers
app.include_router(banking_router)
app.include_router(chat_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
