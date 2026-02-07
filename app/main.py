import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from app.api import banking_router, chat_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bank ABC Voice Agent",
    description="AI-powered banking assistant with 6 customer service flows",
    version="1.1.0",
    docs_url="/docs",

)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporary: Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

# Include routers
app.include_router(banking_router)
app.include_router(chat_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
