# Bank ABC Voice Agent

A full-stack conversational AI platform for banking customer service, featuring intelligent intent routing, safety guardrails, and real-time observability.

## Overview

This project demonstrates an autonomous AI agent capable of handling complex banking conversations across 6 customer service flows. The platform enforces mandatory identity verification before sensitive operations and provides full traceability through LangFuse integration.

## Live Demo

**Frontend**: https://bank-voice-agent-fe.vercel.app/  
**Backend API**: https://bank-voice-agent-production.up.railway.app  
**API Documentation**: https://bank-voice-agent-production.up.railway.app/docs  
**LangFuse Traces**: https://cloud.langfuse.com

## Test Credentials

```
Customer ID: CUST001
PIN: 1234
Account Balance: $15,420.50
Cards: 2 (CARD001 - Credit/Blocked, CARD002 - Debit/Active)
```

## Features

### Implemented Banking Flows

1. **Card & ATM Issues** (Full Implementation)
   - Lost or stolen card reporting
   - Card blocking (irreversible action with confirmation)
   - ATM problem reporting
   - Declined payment assistance

2. **Account Servicing** (Full Implementation)
   - Balance inquiries
   - Transaction history retrieval
   - Profile updates (address changes)
   - Account information requests

3. **Account Opening** (Routing Stub)
   - New account inquiries
   - Document requirements
   - Eligibility questions

4. **Digital App Support** (Routing Stub)
   - Login issues
   - OTP problems
   - App crashes
   - Device registration

5. **Transfers & Bill Payments** (Routing Stub)
   - Money transfer assistance
   - Bill payment help
   - Beneficiary management

6. **Account Closure** (Routing Stub)
   - Closure requests
   - Retention attempts
   - Reason capture

### Security Features

- Mandatory identity verification before accessing sensitive data
- Rate limiting on authentication attempts
- Comprehensive audit logging for all operations
- Session management with secure state handling
- CORS protection for API endpoints

### Observability

- Full LangFuse integration for tracing
- Intent classification logging
- Tool execution tracking
- Error monitoring and debugging
- Real-time trace visualization

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI/LLM**: Groq API (llama-3.3-70b-versatile)
- **Observability**: LangFuse
- **Deployment**: Railway.app
- **Database**: JSON mock data (for POC)

### Frontend
- **Framework**: React + Vite
- **Styling**: TailwindCSS
- **HTTP Client**: Axios
- **Deployment**: Vercel

## Architecture

The system follows a layered architecture:

```
Frontend (React)
    |
    v
REST API (FastAPI)
    |
    v
AI Agent (Intent Classification)
    |
    v
Flow Handlers (Business Logic)
    |
    v
Banking Tools (Mock API)
    |
    v
Mock Database (JSON)
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- Git

### Backend Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd bank-voice-agent
```

2. Create and activate virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
GROQ_API_KEY=your_groq_api_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_BASE_URL=https://cloud.langfuse.com
ENVIRONMENT=development
```

5. Run the backend:
```bash
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment:
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```
VITE_API_BASE_URL=http://localhost:8000
```

4. Run the frontend:
```bash
npm run dev
```

Frontend will be available at: http://localhost:5173

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

**POST /api/chat/**
```json
{
  "message": "what is my balance",
  "customer_id": "CUST001",
  "session_id": "unique-session-id",
  "verified": true
}
```

**POST /api/banking/verify**
```json
{
  "customer_id": "CUST001",
  "pin": "1234"
}
```

## Testing the Application

### End-to-End Test Scenario

1. Open the frontend application
2. Type: "what is my balance"
3. System prompts for identity verification
4. Enter Customer ID: CUST001, PIN: 1234
5. System verifies identity and displays balance: $15,420.50
6. Type: "I lost my credit card"
7. System displays available cards
8. Type: "block CARD002"
9. System blocks the card and confirms action

### Viewing Traces in LangFuse

1. Go to https://cloud.langfuse.com
2. Navigate to your project
3. View traces for "banking-chat" sessions
4. Inspect intent classification, tool calls, and responses

Example traces to review:
- Lost Card scenario (shows card blocking flow)
- Balance Check scenario (shows verification and data retrieval)

## Project Structure

```
bank-voice-agent/
├── app/
│   ├── main.py              # FastAPI application
│   ├── agent/
│   │   └── agent.py         # AI agent with intent classification
│   ├── tools/
│   │   ├── banking.py       # Banking operations (7 functions)
│   │   └── validators.py    # Security decorators
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── api/
│       ├── banking.py       # Banking REST endpoints
│       └── chat.py          # Chat endpoint
├── data/
│   ├── customers.json       # Mock customer data
│   └── transactions.json    # Mock transaction data
├── frontend/
│   └── src/                 # React application
├── documents/               # Documentation
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
└── README.md
```

## Design Decisions and Trade-offs

### 1. Mock Data vs Real Database
**Decision**: Used JSON files for data storage  
**Rationale**: Faster POC development, easier to seed test data  
**Trade-off**: Not production-ready, no concurrent access handling  
**Future**: Migrate to PostgreSQL or MongoDB for production

### 2. Groq API vs Anthropic Claude
**Decision**: Used Groq API with Llama model  
**Rationale**: Free tier availability, fast inference  
**Trade-off**: Less sophisticated reasoning than Claude  
**Future**: Can switch to Claude for production if needed

### 3. LangFuse vs LangSmith
**Decision**: Implemented LangFuse for observability  
**Rationale**: Free tier available, good documentation  
**Trade-off**: Smaller community than LangSmith  
**Future**: Both are viable for production

### 4. No LangGraph/CrewAI
**Decision**: Direct Groq API integration  
**Rationale**: Avoid framework complexity and version conflicts  
**Trade-off**: Less abstraction, more manual orchestration  
**Future**: Consider LangGraph for complex multi-agent scenarios

### 5. Keyword-based Tool Selection
**Decision**: Use keyword matching for tool selection  
**Rationale**: Fast, reliable, no extra LLM calls  
**Trade-off**: Less flexible than LLM-based tool selection  
**Future**: Implement function calling for better tool selection

### 6. Session Management
**Decision**: In-memory session storage  
**Rationale**: Simple for POC, no external dependencies  
**Trade-off**: Sessions lost on server restart  
**Future**: Use Redis for persistent session storage

## Security Considerations

### Implemented
- Identity verification required before sensitive operations
- Rate limiting on authentication attempts
- Audit logging for all banking operations
- CORS protection on API endpoints
- Environment variable management for secrets

### Not Implemented (Future Enhancements)
- JWT-based authentication
- Refresh token mechanism
- IP-based rate limiting
- Request signing
- Encryption at rest for sensitive data

## Known Limitations

1. **Mock Data**: Using JSON files instead of a real database
2. **Partial Implementation**: Only 2 of 6 flows have full business logic
3. **No Voice**: Text-based chat only (voice features planned)
4. **Session Persistence**: In-memory sessions (lost on restart)
5. **No Multi-turn Context**: Agent doesn't maintain conversation history
6. **Simple NLP**: Keyword matching instead of advanced NLU

## Deployment

### Backend (Railway.app)

1. Push code to GitHub
2. Connect Railway to repository
3. Add environment variables in Railway dashboard
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Deploy

### Frontend (Vercel)

1. Push code to GitHub
2. Import project in Vercel
3. Set framework preset: Vite
4. Add environment variable: `VITE_API_BASE_URL`
5. Deploy

## Monitoring and Debugging

### Application Logs
- Railway: View logs in Deployments tab
- Vercel: View logs in Deployments section

### Trace Analysis
- LangFuse: https://cloud.langfuse.com
- View intent classifications
- Inspect tool executions
- Debug errors

### Health Checks
- Backend: https://bank-voice-agent-production.up.railway.app/docs
- Frontend: https://your-frontend.vercel.app

## Future Enhancements

1. Implement remaining 4 flows with full business logic
2. Add voice input/output using Web Speech API
3. Implement conversation history and context
4. Add LLM-based tool selection
5. Migrate to production database
6. Add comprehensive test suite
7. Implement advanced security features
8. Add analytics dashboard
9. Support multiple languages
10. Add file upload for documents

## Contributing

This is a POC project. For production deployment, consider:
- Comprehensive testing (unit, integration, e2e)
- Security audit
- Performance optimization
- Scalability improvements
- Compliance requirements (PCI-DSS, GDPR, etc.)

## License

MIT License

## Support

For issues or questions:
- Check API documentation: /docs endpoint
- Review LangFuse traces for debugging
- Consult technical documentation in /documents folder

## Acknowledgments

- Groq for providing free LLM API access
- LangFuse for observability platform
- Railway and Vercel for free hosting tiers
