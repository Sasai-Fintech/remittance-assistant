"""General enquiry workflow as LangGraph subgraph."""

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from engine.state import AgentState
from copilotkit.langgraph import copilotkit_emit_message
import logging

logger = logging.getLogger(__name__)


async def summarize_general_node(state: AgentState, config: RunnableConfig):
    """Step 1: Provide general greeting."""
    logger.debug("General enquiry subgraph: Starting summarization")
    state["current_workflow"] = "general_enquiry"
    state["workflow_step"] = "summarized"
    
    summary_msg = "I'm here to help! What would you like to know?\n\nHow can I assist you today?"
    state["messages"].append(AIMessage(content=summary_msg))
    await copilotkit_emit_message(config, summary_msg)
    
    # Mark workflow as completed and clear current_workflow
    state["workflow_step"] = "completed"
    state["current_workflow"] = None
    
    logger.debug("General enquiry subgraph: Summarization complete, returning to main graph")
    
    return state


def build_general_enquiry_subgraph():
    """Build and compile the general enquiry subgraph."""
    graph = StateGraph(AgentState)
    graph.add_node("summarize", summarize_general_node)
    graph.add_edge(START, "summarize")
    graph.add_edge("summarize", END)
    return graph.compile()

