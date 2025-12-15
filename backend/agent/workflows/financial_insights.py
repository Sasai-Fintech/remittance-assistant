"""Financial insights workflow - provides insights on incoming, investment, and spending."""

from typing import List, Dict, Any
from langchain_core.runnables import RunnableConfig
from engine.state import AgentState
from .base import BaseWorkflow


class FinancialInsightsWorkflow(BaseWorkflow):
    """Workflow for financial insights and analysis."""
    
    name = "financial_insights"
    intent_keywords = [
        "financial insights", "analyze", "analyse", "insights", "cash flow",
        "spending analysis", "incoming analysis", "investment analysis",
        "analyze incoming", "analyze spends", "analyze investment",
        "analyse incoming", "analyse spends", "analyse investment",
        "show insights", "financial overview", "spending breakdown"
    ]
    description = "Provide financial insights and analysis for incoming, investment, and spending"
    
    async def summarize(self, state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
        """Get user's financial context."""
        return {
            "user_id": state.get("user_id", "demo_user"),
            "account_status": "active"
        }
    
    def get_summary_message(self, context: Dict[str, Any]) -> str:
        """Generate financial insights greeting."""
        return "I can help you analyze your financial data! I can provide insights on your incoming transactions, investments, and spending patterns."
    
    def get_question(self, context: Dict[str, Any]) -> str:
        """Get the question to ask after summary."""
        return "What would you like to analyze?"
    
    def get_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """Get common financial insights suggestions."""
        return [
            "Show cash flow",
            "Analyze incoming",
            "Analyze spends",
            "Analyze investment"
        ]
    
    def get_resolution_guide(self, issue_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get guidance for financial insights requests."""
        guides = {
            "analyze incoming": {
                "message": "I'll analyze your incoming transactions and show you a breakdown by category.",
                "steps": [
                    "Fetching incoming transaction data",
                    "Calculating category breakdown",
                    "Displaying insights with charts"
                ],
                "reference": "",
                "can_resolve": True
            },
            "analyze spends": {
                "message": "I'll analyze your spending patterns and show you where your money is going.",
                "steps": [
                    "Fetching spending transaction data",
                    "Calculating spending categories",
                    "Displaying insights with charts"
                ],
                "reference": "",
                "can_resolve": True
            },
            "analyze investment": {
                "message": "I'll analyze your investment portfolio and show you the distribution.",
                "steps": [
                    "Fetching investment data",
                    "Calculating investment breakdown",
                    "Displaying insights with charts"
                ],
                "reference": "",
                "can_resolve": True
            },
            "show cash flow": {
                "message": "I'll show you a comprehensive cash flow overview with all categories.",
                "steps": [
                    "Fetching all financial data",
                    "Calculating cash flow metrics",
                    "Displaying comprehensive insights"
                ],
                "reference": "",
                "can_resolve": True
            }
        }
        
        issue_lower = issue_type.lower()
        for key, guide in guides.items():
            if key in issue_lower or issue_lower in key:
                return guide
        
        return {
            "message": "I can help you analyze your financial data. What specific insights would you like to see?",
            "steps": ["Specify what you'd like to analyze", "I'll fetch and display the insights"],
            "reference": "",
            "can_resolve": True
        }

