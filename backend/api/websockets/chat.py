import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage

from backend.core.database import get_db
from backend.models.messages import MessageRecord
from backend.agent.graph import graph

router = APIRouter(prefix="/ws", tags=["websocket"])

class ConnectionManager:
    """Manages active WebSocket connections."""
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_event(self, session_id: str, event_type: str, data: dict):
        if session_id in self.active_connections:
            ws = self.active_connections[session_id]
            event = {"type": event_type, **data}
            await ws.send_text(json.dumps(event))

manager = ConnectionManager()

@router.websocket("/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str, db: Session = Depends(get_db)):
    """
    Real-time chat endpoint using WebSockets.
    """
    await manager.connect(session_id, websocket)
    
    try:
        while True:
            # 1. Wait for an incoming message
            data = await websocket.receive_text()
            
            # Parse simple JSON: {"content": "my message"}
            try:
                payload = json.loads(data)
                user_msg_content = payload.get("content", "").strip()
            except json.JSONDecodeError:
                await manager.send_event(session_id, "error", {"message": "Invalid JSON format."})
                continue
                
            if not user_msg_content:
                continue
                
            # 2. Save User message to DB (Optional now, but good for raw logging)
            user_msg = MessageRecord(session_id=session_id, role="user", content=user_msg_content)
            db.add(user_msg)
            db.commit()
            
            # 3. Show typing indicator
            await manager.send_event(session_id, "typing", {"status": "active"})
            
            # 4. Invoke LangGraph
            from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
            
            try:
                # Wrap the invocation in the async checkpointer context
                async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as memory:
                    # Compile specifically for this run with the active memory checkpointer
                    # Since graph is already compiled statically, applying checkpointer requires we compile it again locally or pass it.
                    # Langchain 0.1 allows overriding checkpointer dynamically at compile time
                    from backend.agent.graph import builder
                    runnable_graph = builder.compile(checkpointer=memory)
                    
                    # Provide ONLY the new human message. LangGraph checkpointer will append it to the saved state.
                    response = await runnable_graph.ainvoke(
                        {
                            "messages": [HumanMessage(content=user_msg_content)],
                            "session_id": session_id
                        },
                        config={"configurable": {"thread_id": session_id}}
                    )
                
                # The response will contain the updated messages list
                # The last message is the newly generated AI response
                ai_response_msg = response["messages"][-1]
                ai_content = ai_response_msg.content
                
                # 6. Save AI message to DB
                ai_msg = MessageRecord(session_id=session_id, role="ai", content=ai_content)
                db.add(ai_msg)
                db.commit()
                
                # Hide typing indicator and send the final message via WS
                await manager.send_event(session_id, "typing", {"status": "inactive"})
                await manager.send_event(session_id, "message", {
                    "role": "ai", 
                    "content": ai_content,
                    "id": ai_msg.id
                })
                
            except Exception as e:
                print(f"Error invoking LangGraph: {e}")
                await manager.send_event(session_id, "typing", {"status": "inactive"})
                await manager.send_event(session_id, "error", {"message": "Failed to generate AI response."})

    except WebSocketDisconnect:
        manager.disconnect(session_id)
        print(f"Session {session_id} disconnected.")
