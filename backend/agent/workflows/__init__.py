"""Workflow registry for guided support flows.

This module provides a registry pattern for managing multiple support workflows.
Each workflow handles a specific domain (transactions, refunds, loans, cards, etc.)
and follows a consistent pattern: summarize → identify → resolve → escalate.
"""

from typing import Dict, Type, Optional
from .base import BaseWorkflow

# Import all workflows
from .transaction_help import TransactionHelpWorkflow
from .refund import RefundWorkflow
from .loan_enquiry import LoanEnquiryWorkflow
from .card_issue import CardIssueWorkflow
from .general_enquiry import GeneralEnquiryWorkflow
from .financial_insights import FinancialInsightsWorkflow

# Workflow registry
_workflows: Dict[str, Type[BaseWorkflow]] = {}


def register_workflow(workflow_class: Type[BaseWorkflow]):
    """Register a workflow class."""
    _workflows[workflow_class.name] = workflow_class
    return workflow_class


def get_workflow(name: str) -> Optional[Type[BaseWorkflow]]:
    """Get a workflow by name."""
    return _workflows.get(name)


def get_all_workflows() -> Dict[str, Type[BaseWorkflow]]:
    """Get all registered workflows."""
    return _workflows.copy()


def detect_workflow(user_message: str) -> Optional[str]:
    """Detect which workflow to use based on user message."""
    user_lower = user_message.lower()
    
    # Check workflows in priority order (most specific first)
    priority_order = [
        TransactionHelpWorkflow,
        FinancialInsightsWorkflow,
        RefundWorkflow,
        LoanEnquiryWorkflow,
        CardIssueWorkflow,
        GeneralEnquiryWorkflow,  # Fallback
    ]
    
    for workflow_class in priority_order:
        if workflow_class.matches_intent(user_lower):
            return workflow_class.name
    
    return None


# Auto-register all workflows
def _register_all_workflows():
    """Register all workflow classes."""
    workflows = [
        TransactionHelpWorkflow,
        RefundWorkflow,
        LoanEnquiryWorkflow,
        CardIssueWorkflow,
        GeneralEnquiryWorkflow,
        FinancialInsightsWorkflow,
    ]
    
    for workflow_class in workflows:
        register_workflow(workflow_class)


# Initialize on import
_register_all_workflows()

