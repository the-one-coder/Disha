from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.messages import MessageRecord

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.get("/history")
async def get_chat_history(
    session_id: str = Query(..., description="Unique ID for the chat session"),
    limit: int = Query(50, description="Max number of messages to return"),
    cursor: str = Query(None, description="ISO8601 timestamp to paginate before (e.g., 2026-03-09T15:25:00Z)"),
    db: Session = Depends(get_db)
):
    """
    Fetch paginated chat history for a given session using created_at as cursor.
    """
    from datetime import datetime

    query = db.query(MessageRecord).filter(MessageRecord.session_id == session_id)
    
    if cursor:
        try:
            # Parse the ISO8601 string back to a datetime object
            # Note: handles 'Z' at the end or proper timezone offsets
            cursor_dt = datetime.fromisoformat(cursor.replace('Z', '+00:00'))
            query = query.filter(MessageRecord.created_at < cursor_dt)
        except ValueError:
            pass # Or raise HTTPException(400, "Invalid cursor format")
            
    messages = query.order_by(MessageRecord.created_at.desc()).limit(limit).all()
    
    # Return in chronological order
    messages.reverse()
    
    return {
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    }
