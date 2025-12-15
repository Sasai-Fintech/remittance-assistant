"""Transaction help workflow as LangGraph subgraph."""

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from engine.state import AgentState
from agent.tools import get_transaction_details
from copilotkit.langgraph import copilotkit_emit_message
import logging

logger = logging.getLogger(__name__)


async def summarize_transaction_node(state: AgentState, config: RunnableConfig):
    """Step 1: Get transaction details and summarize.
    
    This node fetches transaction details, updates state with context,
    and provides a summary message. After completion, control returns
    to chat_node for continued conversation and guidance.
    """
    logger.debug("Transaction help subgraph: Starting summarization")
    messages = state.get("messages", [])
    transaction_id = ""
    
    # Extract transaction ID from recent messages
    for msg in reversed(messages[-5:]):
        content = str(msg.content).lower()
        if "txn_" in content:
            import re
            match = re.search(r'txn_\d+', content)
            if match:
                transaction_id = match.group(0)
                break
    
    # Call tool directly (in production, this would go through ToolNode)
    try:
        logger.debug(f"Fetching transaction details for ID: {transaction_id}")
        transaction = get_transaction_details.invoke({
            "user_id": state.get("user_id", "demo_user"),
            "transaction_id": transaction_id
        })
    except Exception as e:
        logger.warning(f"Failed to fetch transaction details: {e}, using fallback")
        # Fallback
        from datetime import datetime, timedelta
        transaction = {
            "id": "txn_1",
            "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "merchant": "Coffee Shop",
            "amount": -50.0,
            "currency": "USD",
            "status": "completed",
            "reference": "532300764753"
        }
    
    # Update state with transaction context
    state["transaction_context"] = transaction
    state["current_workflow"] = "transaction_help"
    state["workflow_step"] = "summarized"
    
    # Format summary message
    amount = abs(transaction.get("amount", 0))
    currency = transaction.get("currency", "USD")
    merchant = transaction.get("merchant", "merchant")
    date = transaction.get("date", "")
    
    from datetime import datetime
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d %b %Y")
    except:
        formatted_date = date
    
    summary_msg = f"Good news: your payment of {amount:.2f} {currency} to {merchant} on {formatted_date} was successful.\n\nUTR: {transaction.get('reference', 'N/A')}\n\nTell us what's wrong"
    
    # Add summary message
    state["messages"].append(AIMessage(content=summary_msg))
    await copilotkit_emit_message(config, summary_msg)
    
    # Mark workflow as completed and clear current_workflow to allow new intent detection
    # The workflow context is preserved in transaction_context for chat_node to use
    state["workflow_step"] = "completed"
    state["current_workflow"] = None  # Clear to allow new workflows
    
    logger.debug("Transaction help subgraph: Summarization complete, returning to main graph")
    
    return state


def build_transaction_help_subgraph():
    """Build and compile the transaction help subgraph.
    
    This subgraph summarizes the transaction and returns control to chat_node.
    Guidance is handled in chat_node via the system message, which provides
    context-aware resolution steps based on the user's issue description.
    """
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("summarize", summarize_transaction_node)
    
    # Add edges
    graph.add_edge(START, "summarize")
    graph.add_edge("summarize", END)  # After summarize, return to main graph for user response
    
    return graph.compile()

