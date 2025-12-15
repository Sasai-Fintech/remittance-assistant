"""Loan enquiry workflow as LangGraph subgraph."""

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from engine.state import AgentState
from copilotkit.langgraph import copilotkit_emit_message
import logging

logger = logging.getLogger(__name__)


async def summarize_loan_node(state: AgentState, config: RunnableConfig):
    """Step 1: Get loan information and summarize."""
    logger.debug("Loan enquiry subgraph: Starting summarization")
    # Placeholder - in production, call loan tools
    state["loan_context"] = {
        "active_loans": [],
        "loan_eligibility": {
            "eligible": True,
            "max_amount": 50000,
            "interest_rate": 12.5
        }
    }
    state["current_workflow"] = "loan_enquiry"
    state["workflow_step"] = "summarized"
    
    summary_msg = "I can help you with loan enquiries, applications, and managing your existing loans.\n\nWhat would you like to know about loans?"
    state["messages"].append(AIMessage(content=summary_msg))
    await copilotkit_emit_message(config, summary_msg)
    
    # Mark workflow as completed and clear current_workflow
    state["workflow_step"] = "completed"
    state["current_workflow"] = None
    
    logger.debug("Loan enquiry subgraph: Summarization complete, returning to main graph")
    
    return state


def build_loan_enquiry_graph():
    """Build and compile the loan enquiry subgraph."""
    graph = StateGraph(AgentState)
    graph.add_node("summarize", summarize_loan_node)
    graph.add_edge(START, "summarize")
    graph.add_edge("summarize", END)
    return graph.compile()

