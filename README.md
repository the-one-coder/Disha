# Disha AI Health Coach

A full-stack web application that simulates a WhatsApp-like chat interface where an AI health coach answers user questions. The app handles ongoing, single-session chats with automatic context overflow management, long-term memory retrieval, and real-time medical/protocol matching.

## Architecture Overview

The backend is built with FastAPI and implemented using a modular, enterprise-level directory structure:
- `backend/core/` & `backend/models/`: Database connection and SQLAlchemy schema definitions.
- `backend/api/`: FastAPI REST routers (`/api/chat/history`) and WebSocket managers (`/ws/chat/{session_id}`).
- `backend/agent/`: LangGraph orchestrator using Google's Gemini API, managing state, context summarization, and the health coach persona.

## Running Locally

*(Detailed instructions to run the application locally will be added here once development is further along)*

### Prerequisites
- Python 3.10+
- `pip install -r requirements.txt`

### Environment Variables
You must configure the following environment variables:
- `GEMINI_API_KEY`: Your Google Gemini API Key required for the LLM features.

### Database Setup
*(Instructions for DB migrations and seed scripts will be added here)*

## LLM System Details

**Provider:** Google Gemini (`gemini-1.5-pro`)  
**Orchestration:** LangChain / LangGraph  
**Context Management:** Context overflow is managed by summarizing older conversation history using an LLM when token limits are reached. Gemini is configured with `max_output_tokens=1024` to ensure concise responses.

## Trade-offs & If I had more time...
*(Will be populated at the end of the project)*
