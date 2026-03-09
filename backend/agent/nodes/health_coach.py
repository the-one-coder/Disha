from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.agent.state import AgentState

import os

# Initialize the LLM (Gemini)
# Expects GEMINI_API_KEY environment variable to be set
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=0.7,
    max_output_tokens=1024
) if "GEMINI_API_KEY" in os.environ else None

def health_coach_node(state: AgentState):
    """
    The main LLM node that responds to the user.
    """
    messages = state["messages"]
    
    # Prepend a system prompt to define the persona
    system_prompt = SystemMessage(
        content="""You are a friendly, empathetic AI Health Coach. 
You act like you are chatting with a user on WhatsApp. Keep your responses concise, conversational, and helpful.
Do NOT give formal medical diagnoses. Suggest general wellness tips and recommend seeing a doctor for serious issues.
Your goal is to be a supportive conversational partner for health and wellness."""
    )
    
    # Combine system prompt with history
    invoke_messages = [system_prompt] + messages
    
    # Call Gemini
    response = llm.invoke(invoke_messages)
    
    return {"messages": [response]}
