from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone
import uuid

from backend.core.database import Base, engine

class MessageRecord(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, index=True)
    role = Column(String)  # 'user' or 'ai'
    content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

# Create the tables (could be moved to a migration script later)
Base.metadata.create_all(bind=engine)
