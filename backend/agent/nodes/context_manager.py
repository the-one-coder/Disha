import os
import tiktoken
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, RemoveMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.agent.state import AgentState

# We use the standard cl100k_base encoding as a proxy for token counts
encoding = tiktoken.get_encoding("cl100k_base")

# Gemini 1.5 Pro has a 2M token limit. 
# We'll set a much lower limit for the simple chat app to respond fast, e.g., 1,00,000 tokens
MAX_ALLOWED_TOKENS = 100000 
MAX_OUTPUT_TOKENS = 1024
THRESHOLD_TOKENS = int(MAX_ALLOWED_TOKENS * 0.70) # 70,000 tokens

def count_tokens(text: str) -> int:
    return len(encoding.encode(text))

def context_manager_node(state: AgentState):
    """
    Manages context window by checking the token limit.
    If the limit is exceeded, it uses the LLM to summarize the oldest messages.
    """
    messages = state["messages"]
    
    # Calculate current token size
    current_tokens = sum(count_tokens(m.content) for m in messages if isinstance(m.content, str))
    
    # Check if (Current Size + Max Output) exceeds our 70% threshold
    if (current_tokens + MAX_OUTPUT_TOKENS) > THRESHOLD_TOKENS:
        # We need to summarize. We will leave the 5 most recent messages untouched
        # and summarize everything before that.
        if len(messages) <= 6:
            # Not enough messages to meaningfully summarize without losing immediate context
            return {"messages": []} 
            
        recent_messages = messages[-5:]
        older_messages = messages[:-5]
        
        # Prepare summarization prompt
        summary_prompt = "Summarize the following conversation history focusing on the user's long-term health constraints, goals, and any medical protocols discussed. Be concise:\n\n"
        for msg in older_messages:
            role = "User" if isinstance(msg, HumanMessage) else "AI"
            summary_prompt += f"{role}: {msg.content}\n\n"
            
        # Call the LLM to summarize
        llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0.3)
        summary_response = llm.invoke([HumanMessage(content=summary_prompt)])
        
        # Create the new summary message to be placed at the start
        summary_msg = SystemMessage(content=f"Previous Conversation Summary: {summary_response.content}")
        
        # In LangGraph, to remove old messages from the state under the 'add' reducer,
        # we return a list of RemoveMessage objects with the IDs of the messages to delete.
        delete_messages = [RemoveMessage(id=m.id) for m in older_messages if m.id]
        
        return {"messages": delete_messages + [summary_msg]}

    # If within limits, do nothing
    return {"messages": []}
