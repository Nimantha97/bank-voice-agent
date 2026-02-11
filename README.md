# Bank ABC Voice Agent

A full-stack conversational AI platform for banking customer service, featuring intelligent intent routing, safety guardrails, and real-time observability.

## Overview

This project demonstrates an autonomous AI agent capable of handling complex banking conversations across 6 customer service flows. The platform enforces mandatory identity verification before sensitive operations and provides full traceability through LangFuse integration.

**Project Scope**: This is a Proof of Concept (POC) implementation focused on demonstrating:
- AI agent architecture and intent classification
- Multi-flow conversation handling
- Security patterns (identity verification, rate limiting)
- Observability and tracing infrastructure
- Full-stack integration (React frontend + FastAPI backend)
- Production deployment capabilities

The POC uses JSON mock data to prioritize rapid development and easy testing. The architecture is designed with clear separation of concerns, allowing straightforward migration to production-grade databases without affecting business logic.

## Live Demo

**Frontend**: https://bank-voice-agent-fe-oqa1.vercel.app/   
**Backend API Documentation**: https://bank-voice-agent-production.up.railway.app/docs  
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
- **Voice AI**: Groq Whisper (STT) + Orpheus (TTS)
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

Edit `.env` and add related API keys:
```
GROQ_API_KEY=ygroq_api_key
LANGFUSE_SECRET_KEY=langfuse_secret_key
LANGFUSE_PUBLIC_KEY=langfuse_public_key
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
- Health Check: http://localhost:8000/health

For detailed API examples with curl commands, see [API Examples](documents/API_EXAMPLES.md).

### Key Endpoints

#### Text Chat Endpoints

**POST /api/chat/**

Text-based conversational interface. Processes text messages through the AI agent and returns text responses.

```json
{
  "message": "what is my balance",
  "customer_id": "CUST001",
  "session_id": "unique-session-id",
  "verified": true
}
```

#### Voice AI Endpoints

**POST /api/voice/transcribe**

Converts audio to text using Groq Whisper. Upload audio file (WAV, MP3, M4A) and receive transcribed text.

```bash
curl -X POST "http://localhost:8000/api/voice/transcribe" \
  -F "audio=@recording.wav"
```

Response:
```json
{
  "text": "what is my account balance",
  "language": "en"
}
```

**POST /api/voice/synthesize**

Converts text to speech using Groq Orpheus. Returns audio file (WAV format).

```bash
curl -X POST "http://localhost:8000/api/voice/synthesize" \
  -F "text=Your balance is fifteen thousand dollars" \
  -F "voice=autumn" \
  --output response.wav
```

Available voices: `autumn`, `diana`, `hannah`, `austin`, `daniel`, `troy`

**POST /api/voice/chat**

Voice-enabled chat interface. Accepts text input (typically from transcription) and returns text output (for synthesis). Uses the same AI agent logic as /api/chat but optimized for voice workflows.

```json
{
  "message": "what is my balance",
  "customer_id": "CUST001",
  "verified": true,
  "session_id": "unique-session-id"
}
```

Response:
```json
{
  "text_response": "Your Savings account has a balance of $15,420.50",
  "session_id": "unique-session-id",
  "requires_verification": false,
  "flow": "account_servicing"
}
```

**GET /api/voice/health**

Voice AI service health check.

```json
{
  "status": "healthy",
  "service": "voice-ai",
  "features": {
    "speech_to_text": "whisper-large-v3-turbo",
    "text_to_speech": "canopylabs/orpheus-v1-english",
    "voice_chat": "enabled"
  }
}
```

#### Authentication Endpoints

**POST /api/banking/verify**
```json
{
  "customer_id": "CUST001",
  "pin": "1234"
}
```

**GET /health**
```json
{
  "status": "healthy",
  "service": "bank-voice-agent",
  "version": "1.1.0"
}
```

### Chat vs Voice Endpoints

The platform provides two parallel interfaces for the same banking agent:

**Text Chat (/api/chat)**
- Direct text input and output
- Designed for web chat interfaces, messaging apps, or API integrations
- Single endpoint handles the complete conversation flow
- Returns formatted text responses ready for display

**Voice AI (/api/voice/\*)**
- Three-step workflow: transcribe audio, process through agent, synthesize response
- Designed for voice-based interfaces like phone systems or voice assistants
- Modular endpoints allow flexible integration (use transcription only, synthesis only, or full pipeline)
- /api/voice/chat uses the same agent logic as /api/chat but returns responses optimized for text-to-speech conversion

Both interfaces share the same:
- AI agent and intent classification logic
- Banking tools and business logic
- Security and verification requirements
- Session management and audit logging

The separation allows clients to choose the appropriate interface without duplicating backend logic.


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

### LangFuse Trace Evidence

The following traces demonstrate the AI agent's execution flow, including intent classification, tool calls, and response generation. Each trace provides full visibility into the system's decision-making process.

**Live Trace Links:**

- **Balance Check**: [View Trace](https://cloud.langfuse.com/project/cmlbasbjr02htad07y2plt3do/traces/b922811043fa16a0f4433812e8c21d68?timestamp=2026-02-10T09%253A57%253A48.615Z)
  - Demonstrates identity verification flow
  - Shows get_account_balance tool execution
  - Displays account information retrieval

- **Recent Transactions**: [View Trace](https://cloud.langfuse.com/project/cmlbasbjr02htad07y2plt3do/traces/c46dc372ec02860a864c5f028ea8386f?timestamp=2026-02-09T04%253A52%253A15.526Z)
  - Shows transaction history retrieval
  - Demonstrates get_recent_transactions tool call
  - Displays formatted transaction list

- **Lost Credit Card**: [View Trace](https://cloud.langfuse.com/project/cmlbasbjr02htad07y2plt3do/traces/a93b406449ffdc764f1af04152f0be87?timestamp=2026-02-10T09%253A58%253A11.587Z)
  - Shows intent classification for card issues
  - Demonstrates get_customer_cards tool execution
  - Displays card listing and selection flow

- **Block Card (CARD002)**: [View Trace](https://cloud.langfuse.com/project/cmlbasbjr02htad07y2plt3do/traces/b09eee5815e3d618909785c1c52322c0?timestamp=2026-02-10T09%253A58%253A27.370Z)
  - Shows complete card blocking workflow
  - Demonstrates block_card tool execution
  - Displays confirmation and audit logging

**Trace Screenshots:**

For quick reference without requiring LangFuse access, screenshots of key traces are available in the `/documents` folder:

- `langfuse-trace-balance-check.png` - Balance inquiry with verification
- `langfuse-trace-lost-card.png` - Lost card reporting flow
- `langfuse-trace-block-card.png` - Card blocking execution
- `langfuse-trace-transactions.png` - Transaction history retrieval

Each trace includes:
- User input message
- Intent classification result
- Tool/function calls with parameters
- Execution timing and performance metrics
- Final response output
- Error handling (if applicable)

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
│       ├── chat.py          # Text chat endpoint
│       └── voice.py         # Voice AI endpoints (STT/TTS/chat)
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

### 1. Data Layer: JSON Mock Data vs Database
**Decision**: Used JSON files for data storage in this POC  
**Rationale**:  
- Faster POC development and iteration cycles
- Zero infrastructure dependencies for reviewers to test locally
- Simplified deployment without database provisioning
- Easier to seed consistent test data across environments
- Demonstrates business logic and AI integration without database complexity

**Trade-off**: Not suitable for production use due to:
- No concurrent access handling or transaction support
- No data persistence across server restarts
- Limited scalability and query performance
- No relational integrity constraints

**Production Migration Path**:  
The current architecture uses a repository pattern that abstracts data access through `app/tools/banking.py`. This design allows for straightforward migration to a real database:
```python
# Current: JSON file access
def get_customer(customer_id: str):
    with open('data/customers.json') as f:
        customers = json.load(f)
    return customers.get(customer_id)

# Future: Database access (same interface)
def get_customer(customer_id: str):
    return db.query(Customer).filter_by(id=customer_id).first()
```
Recommended production stack: PostgreSQL with SQLAlchemy ORM, maintaining the same function signatures to minimize code changes.

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
3. **Session Persistence**: In-memory sessions (lost on restart)
4. **Limited Context**: Agent doesn't maintain multi-turn conversation history
5. **Keyword-Based Routing**: Uses pattern matching instead of LLM-based tool selection

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

## Contributing

This is a POC project. For production deployment, consider:
- Comprehensive testing (unit, integration, e2e)
- Security audit
- Performance optimization
- Scalability improvements
- Compliance requirements (PCI-DSS, GDPR, etc.)


## Support

For issues or questions:
- Check API documentation: /docs endpoint
- Review LangFuse traces for debugging
- Consult technical documentation in /documents folder

## Acknowledgments

- Groq for providing free LLM API access
- LangFuse for observability platform
- Railway and Vercel for free hosting tiers
