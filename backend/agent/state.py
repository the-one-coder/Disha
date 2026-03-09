from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """The state of the agent, containing the conversation history and current session context."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    session_id: str
