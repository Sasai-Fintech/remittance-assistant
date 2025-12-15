"""Card issue workflow as LangGraph subgraph."""

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from engine.state import AgentState
from copilotkit.langgraph import copilotkit_emit_message
import logging

logger = logging.getLogger(__name__)


async def summarize_card_node(state: AgentState, config: RunnableConfig):
    """Step 1: Get card information and summarize."""
    logger.debug("Card issue subgraph: Starting summarization")
    # Placeholder - in production, call card tools
    state["card_context"] = {
        "cards": [
            {
                "id": "card_1",
                "type": "debit",
                "last_four": "1234",
                "status": "active",
                "expiry": "12/26"
            }
        ]
    }
    state["current_workflow"] = "card_issue"
    state["workflow_step"] = "summarized"
    
    card = state["card_context"]["cards"][0]
    summary_msg = f"I can see you have a {card.get('type', 'card')} card ending in {card.get('last_four', '****')}. How can I help you with your card?\n\nWhat issue are you experiencing with your card?"
    state["messages"].append(AIMessage(content=summary_msg))
    await copilotkit_emit_message(config, summary_msg)
    
    # Mark workflow as completed and clear current_workflow
    state["workflow_step"] = "completed"
    state["current_workflow"] = None
    
    logger.debug("Card issue subgraph: Summarization complete, returning to main graph")
    
    return state


def build_card_issue_subgraph():
    """Build and compile the card issue subgraph."""
    graph = StateGraph(AgentState)
    graph.add_node("summarize", summarize_card_node)
    graph.add_edge(START, "summarize")
    graph.add_edge("summarize", END)
    return graph.compile()

