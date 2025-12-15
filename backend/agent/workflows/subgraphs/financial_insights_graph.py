"""Financial insights workflow as LangGraph subgraph."""

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from engine.state import AgentState
from copilotkit.langgraph import copilotkit_emit_message
import logging

logger = logging.getLogger(__name__)


async def summarize_financial_insights_node(state: AgentState, config: RunnableConfig):
    """Step 1: Provide financial insights summary.
    
    This node provides a summary message about available financial insights.
    After completion, control returns to chat_node for continued conversation.
    """
    logger.debug("Financial insights subgraph: Starting summarization")
    
    # Update state with workflow context
    state["financial_insights_context"] = {
        "user_id": state.get("user_id", "demo_user"),
        "available_categories": ["incoming", "investment", "spends"]
    }
    state["current_workflow"] = "financial_insights"
    state["workflow_step"] = "summarized"
    
    # Create summary message
    summary_msg = "I can help you analyze your financial data! I can provide:\n\n" \
                  "• **Cash Flow Overview** - See a bar chart with Incoming, Investment, and Spends totals\n" \
                  "• **Detailed Breakdowns** - Analyze specific categories with donut charts:\n" \
                  "  - Incoming transactions breakdown\n" \
                  "  - Investment portfolio breakdown\n" \
                  "  - Spending patterns breakdown\n\n" \
                  "What would you like to see?"
    
    # Add summary message
    state["messages"].append(AIMessage(content=summary_msg))
    await copilotkit_emit_message(config, summary_msg)
    
    # Mark workflow as completed and clear current_workflow
    state["workflow_step"] = "completed"
    state["current_workflow"] = None
    
    logger.debug("Financial insights subgraph: Summarization complete, returning to main graph")
    
    return state


def build_financial_insights_subgraph():
    """Build and compile the financial insights subgraph.
    
    This subgraph provides a summary of available financial insights and returns control to chat_node.
    The chat_node will handle tool calls to fetch and display insights based on user requests.
    """
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("summarize", summarize_financial_insights_node)
    
    # Add edges
    graph.add_edge(START, "summarize")
    graph.add_edge("summarize", END)  # After summarize, return to main graph for user response
    
    return graph.compile()

