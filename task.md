# Project: Mini AI Health Coach (Curelink Assignment)

## 1. Project Overview
[cite_start]Build a full-stack web application that simulates a WhatsApp-like chat interface where an AI health coach answers user questions[cite: 14]. [cite_start]The app must handle ongoing, single-session chats with automatic context overflow management, long-term memory retrieval, and real-time medical/protocol matching[cite: 15, 16, 22]. 

## 2. Tech Stack
* [cite_start]**Backend Framework:** Python with FastAPI for async endpoints and WebSocket support[cite: 8, 9].
* **AI Orchestration:** LangChain and LangGraph.
* [cite_start]**LLM API:** Google Gemini API via `langchain-google-genai`[cite: 14, 30].
* **Database & Persistence:** PostgreSQL or SQLite. [cite_start]Use LangGraph's built-in checkpointer (`AsyncSqliteSaver` or `AsyncPostgresSaver`) for conversation state persistence[cite: 10, 29].
* **Vector Store:** `langchain-chroma` or pgvector (via `langchain-postgres`) to handle RAG for medical protocols and long-term memory.
* [cite_start]**Frontend:** Vanilla JS / HTML / CSS (or simple React/Vue) emphasizing clean backend access patterns[cite: 9].

## 3. Core Features to Implement

### A. Chat Interface & UX
* [cite_start]Implement a single-session chat UI (no "start" or "delete" session buttons)[cite: 15].
* [cite_start]The UX must feel like WhatsApp, not ChatGPT[cite: 23, 24].
* [cite_start]Implement auto-loading of old chat history when the user scrolls upwards[cite: 19, 27].
* [cite_start]Include UI/UX elements for typing indicators[cite: 27].

### B. LangGraph Architecture & Context Management
* **State Graph:** Define a LangGraph `StateGraph` with a `messages` state (using `add_messages` reducer).
* [cite_start]**Onboarding Node:** If the chat history is empty, route to an onboarding node/agent to gather user context[cite: 20, 21].
* [cite_start]**Context Overflow:** Implement a custom LangGraph node to trim or summarize the `messages` list before calling the LLM to prevent exceeding Gemini's context limits[cite: 16, 32].
* **RAG / Memory Tooling:** Equip the LangGraph agent with tools to query the vector store for:
    1. [cite_start]Older long-term memories of the user[cite: 34].
    2. [cite_start]Common protocols (e.g., handling fever, stomach ache, or refund policies) dynamically matched to the user's query[cite: 35].

### C. Backend Access Patterns & APIs
* [cite_start]Design APIs that specifically support standard chat features (paginated history loading, real-time message streaming, typing indicators)[cite: 27, 28].
* [cite_start]Persist all message history reliably in the database via LangGraph's checkpointer[cite: 29].
* [cite_start]Ensure the code is robust and handles bad or large inputs gracefully[cite: 36].

## 4. Required Database Entities
Please scaffold the following basic schema:
1. **User:** Tracks the user identity.
2. **LangGraph Checkpoint Tables:** Auto-generated tables by LangGraph to store thread state and message history.
3. **Protocol/Memory (Vector Store):** Stores textual protocols and memories with vector embeddings to allow semantic search.

## 5. README Generation Instructions
[cite_start]Generate a comprehensive `README.md` containing[cite: 49]:
* [cite_start]Step-by-step instructions to run the backend and frontend locally[cite: 50].
* [cite_start]Instructions on how to set up the DB (migrations/seed scripts)[cite: 51].
* [cite_start]How to configure environment variables (e.g., `GEMINI_API_KEY`)[cite: 52].
* [cite_start]A short architecture overview detailing layers, modules, and the LangGraph flow[cite: 54, 55, 56].
* [cite_start]Notes on the LLM architecture: provider used, prompting strategy, and how context overflow was handled[cite: 57, 58, 60].
* [cite_start]A "Trade-offs & If I had more time..." section[cite: 61].