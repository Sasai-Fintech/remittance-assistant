"""Refund workflow as LangGraph subgraph."""

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from engine.state import AgentState
from copilotkit.langgraph import copilotkit_emit_message
import logging

logger = logging.getLogger(__name__)


async def summarize_refund_node(state: AgentState, config: RunnableConfig):
    """Step 1: Get refund-eligible transactions and summarize."""
    logger.debug("Refund subgraph: Starting summarization")
    # Placeholder - in production, call refund tools
    state["refund_context"] = {
        "refund_eligible_transactions": [
            {
                "id": "txn_1",
                "merchant": "Coffee Shop",
                "amount": 50.0,
                "date": "2025-11-22",
                "refund_status": "eligible"
            }
        ]
    }
    state["current_workflow"] = "refund"
    state["workflow_step"] = "summarized"
    
    summary_msg = "You have 1 transaction(s) that may be eligible for refund. Let me help you with your refund request.\n\nWhat type of refund are you looking for?"
    state["messages"].append(AIMessage(content=summary_msg))
    await copilotkit_emit_message(config, summary_msg)
    
    # Mark workflow as completed and clear current_workflow
    state["workflow_step"] = "completed"
    state["current_workflow"] = None
    
    logger.debug("Refund subgraph: Summarization complete, returning to main graph")
    
    return state


def build_refund_subgraph():
    """Build and compile the refund subgraph."""
    graph = StateGraph(AgentState)
    graph.add_node("summarize", summarize_refund_node)
    graph.add_edge(START, "summarize")
    graph.add_edge("summarize", END)
    return graph.compile()

