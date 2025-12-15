"""LangGraph subgraphs for guided support workflows."""

from typing import Optional

# Import subgraph builders
from .transaction_help_graph import build_transaction_help_subgraph
from .refund_graph import build_refund_subgraph
from .loan_enquiry_graph import build_loan_enquiry_graph
from .card_issue_graph import build_card_issue_subgraph
from .general_enquiry_graph import build_general_enquiry_subgraph
from .financial_insights_graph import build_financial_insights_subgraph

def detect_workflow_intent(user_message: str) -> Optional[str]:
    """
    Detect which workflow subgraph to use based on user message.
    Returns workflow name or None.
    """
    user_lower = user_message.lower()
    
    # Priority order: most specific first
    if any(kw in user_lower for kw in ["help with transaction", "transaction issue", "payment problem", "transaction to", "payment to"]):
        return "transaction_help"
    elif any(kw in user_lower for kw in ["financial insights", "analyze", "analyse", "insights", "cash flow", "spending analysis", "incoming analysis", "investment analysis", "analyze incoming", "analyze spends", "analyze investment", "show insights", "financial overview", "spending breakdown"]):
        return "financial_insights"
    elif any(kw in user_lower for kw in ["refund", "money back", "return payment", "get refund"]):
        return "refund"
    elif any(kw in user_lower for kw in ["loan", "borrow", "credit", "apply for loan", "loan application"]):
        return "loan_enquiry"
    elif any(kw in user_lower for kw in ["card", "debit card", "credit card", "card blocked", "card not working"]):
        return "card_issue"
    elif any(kw in user_lower for kw in ["help", "question", "enquiry", "information", "how to"]):
        return "general_enquiry"
    
    return None

def get_workflow_subgraph(workflow_name: str):
    """
    Get the compiled subgraph for a workflow.
    Returns None if workflow not found.
    """
    # Subgraph builders
    subgraph_builders = {
        "transaction_help": build_transaction_help_subgraph,
        "refund": build_refund_subgraph,
        "loan_enquiry": build_loan_enquiry_graph,
        "card_issue": build_card_issue_subgraph,
        "general_enquiry": build_general_enquiry_subgraph,
        "financial_insights": build_financial_insights_subgraph,
    }
    
    builder = subgraph_builders.get(workflow_name)
    if builder:
        return builder()
    
    return None

