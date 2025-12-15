"""Shared nodes for workflow subgraphs."""

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from engine.state import AgentState
from copilotkit.langgraph import copilotkit_emit_message


async def escalate_to_ticket_node(state: AgentState, config: RunnableConfig):
    """Shared node for escalating to ticket creation."""
    state["workflow_step"] = "escalating"
    # The main graph will handle ticket creation
    # This node just marks the state
    return state


async def check_resolution_node(state: AgentState, config: RunnableConfig):
    """Check if issue has been resolved or needs escalation."""
    messages = state.get("messages", [])
    last_user_msg = None
    
    for msg in reversed(messages):
        from langchain_core.messages import HumanMessage
        if isinstance(msg, HumanMessage):
            last_user_msg = str(msg.content).lower()
            break
    
    if last_user_msg:
        # Check if user indicates resolution
        resolved_keywords = ["resolved", "fixed", "worked", "thanks", "okay", "got it"]
        if any(kw in last_user_msg for kw in resolved_keywords):
            state["resolution_attempted"] = True
            resolved_msg = "Great! I'm glad we could help. Is there anything else you need?"
            state["messages"].append(AIMessage(content=resolved_msg))
            await copilotkit_emit_message(config, resolved_msg)
            return state
    
    # If not resolved, mark for potential escalation
    state["resolution_attempted"] = False
    return state

