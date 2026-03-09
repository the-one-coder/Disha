# Implementation Plan & ProgressTracker

This file serves as a persistent reference for tracking what has been completed and what still needs to be done based on the `task.md` requirements.

## Phase 1: Backend Focus

### Completed (Backend)
- **FastAPI Setup:** Basic FastAPI application structure is inplace, utilizing a modular router pattern (`backend/api/` and `backend/main.py`).
- **Websocket for Chat:** Real-time chat endpoint (`/ws/chat/{session_id}`) is implemented with typing indicators.
- **Chat History API:** Paginated chat history endpoint (`/api/chat/history`) is implemented.
- **Basic LangGraph:** Simple `StateGraph` with a `context_manager` node and a `health_coach` node using Gemini API is implemented within the `backend/agent/` module.
- **Modular DB Layer:** Core database engine and `MessageRecord` models are set up in `backend/core/` and `backend/models/`.
- **LangGraph Checkpointer:** Implemented LangGraph's built-in checkpointer (`AsyncSqliteSaver`) for conversation state persistence on every WebSocket interaction.
- **Context Summarizer Node:** Updated the `context_manager` node to use `tiktoken` to estimate context overflow. `MAX_ALLOWED_TOKENS=100,000`, threshold is 70% (70K tokens). Check: `current_tokens + max_output_tokens (1024) > threshold`. If so, it calls the LLM to summarize the oldest messages via `RemoveMessage`.

### To Do (Backend)
- [ ] **Database Schema Updates:** Add a `User` entity to track user identity.
- [ ] **Onboarding Node:** Add an Onboarding node/agent to LangGraph to gather user context when chat history is empty.
- [ ] **Vector Store Integration:** Set up `langchain-chroma` (or `langchain-postgres`) to handle RAG for medical protocols and long-term memory.
- [ ] **Agent Tools (RAG/Memory):** Equip the LangGraph agent with tools to:
  - Query older long-term memories of the user.
  - Query common protocols dynamically matched to the user's query.

## Phase 2: Frontend Focus

### Completed (Frontend)
- **Project Setup:** Plain HTML/CSS/JS app in `frontend/` directory. Served via FastAPI's `StaticFiles` mount at `/app`.
- **Chat UI:** WhatsApp-style interface with user/AI message bubbles and Markdown rendering.
- **WebSocket Integration:** Real-time messaging with typing indicator and auto-reconnect.
- **History Autoload:** Scroll-to-top triggers paginated `/api/chat/history` fetch (cursor-based, `created_at` timestamp). Preserves scroll position after loading.

### To Do (Frontend)
- [ ] Improve session management (e.g., named sessions, session picker).

## Phase 3: Documentation & Polish
- [ ] **Generate README:** Include run instructions, DB setup, Env variables config, architecture overview, LLM details, and trade-offs.
