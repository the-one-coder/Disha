from langgraph.graph import StateGraph, START, END

from backend.agent.state import AgentState
from backend.agent.nodes.context_manager import context_manager_node
from backend.agent.nodes.health_coach import health_coach_node

# Build the Graph
builder = StateGraph(AgentState)

builder.add_node("context_manager", context_manager_node)
builder.add_node("health_coach", health_coach_node)

builder.add_edge(START, "context_manager")
builder.add_edge("context_manager", "health_coach")
builder.add_edge("health_coach", END)

# Compile graph without a static checkpointer (we'll pass it dynamically in the route)
graph = builder.compile()

# Example usage to invoke the graph:
# response = await graph.ainvoke(
#     {"messages": [HumanMessage(content="Hello!")]},
#     config={"configurable": {"thread_id": "session_123"}}
# )
