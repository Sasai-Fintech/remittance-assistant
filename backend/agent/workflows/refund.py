"""Refund workflow - handles refund requests and enquiries."""

from typing import List, Dict, Any
from langchain_core.runnables import RunnableConfig
from engine.state import AgentState
from .base import BaseWorkflow


class RefundWorkflow(BaseWorkflow):
    """Workflow for handling refund requests."""
    
    name = "refund"
    intent_keywords = [
        "refund", "money back", "return payment", "get refund",
        "refund request", "cancel payment", "reverse payment"
    ]
    description = "Handle refund requests and enquiries"
    
    async def summarize(self, state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
        """Get refund-eligible transactions or refund status."""
        # In production, this would call a tool to get refund-eligible transactions
        # For now, return mock data
        return {
            "refund_eligible_transactions": [
                {
                    "id": "txn_1",
                    "merchant": "Coffee Shop",
                    "amount": 50.0,
                    "date": "2025-11-22",
                    "refund_status": "eligible",
                    "refund_deadline": "2025-12-22"
                }
            ],
            "user_id": state.get("user_id", "demo_user")
        }
    
    def get_summary_message(self, context: Dict[str, Any]) -> str:
        """Generate refund summary message."""
        transactions = context.get("refund_eligible_transactions", [])
        if transactions:
            count = len(transactions)
            return f"You have {count} transaction(s) that may be eligible for refund. Let me help you with your refund request."
        return "I can help you with refund requests. What would you like to know?"
    
    def get_question(self, context: Dict[str, Any]) -> str:
        """Get the question to ask after summary."""
        return "What type of refund are you looking for?"
    
    def get_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """Get common refund-related suggestions."""
        return [
            "Refund for cancelled order",
            "Refund for service not received",
            "Refund for wrong amount",
            "Check refund status",
            "Refund policy information"
        ]
    
    def get_resolution_guide(self, issue_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get resolution guidance for refund issues."""
        transactions = context.get("refund_eligible_transactions", [])
        
        guides = {
            "refund for cancelled order": {
                "message": "For cancelled orders, refunds are typically processed automatically within 5-7 business days. If it's been longer, contact the merchant directly.",
                "steps": [
                    "Check your transaction history for refund status",
                    "Wait 5-7 business days for automatic processing",
                    "If not received, contact the merchant with transaction details"
                ],
                "reference": transactions[0].get("id", "") if transactions else "",
                "can_resolve": True
            },
            "refund for service not received": {
                "message": "Contact the merchant directly with your transaction details. They can process the refund or you can dispute the charge.",
                "steps": [
                    "Gather transaction details (date, amount, merchant)",
                    "Contact merchant customer support",
                    "If merchant unresponsive, you can dispute the charge"
                ],
                "reference": transactions[0].get("id", "") if transactions else "",
                "can_resolve": True
            },
            "refund for wrong amount": {
                "message": "Contact the merchant to correct the amount. If they agree, they can process a partial refund.",
                "steps": [
                    "Calculate the correct amount vs charged amount",
                    "Contact merchant with transaction details",
                    "Request partial refund for difference"
                ],
                "reference": transactions[0].get("id", "") if transactions else "",
                "can_resolve": True
            },
            "check refund status": {
                "message": "I can check the status of your refund. Please provide the transaction ID or I can show your recent transactions.",
                "steps": [
                    "Provide transaction ID or date",
                    "I'll check the refund status",
                    "If pending, I'll provide expected timeline"
                ],
                "reference": "",
                "can_resolve": True
            },
            "refund policy information": {
                "message": "Our refund policy: Full refunds available within 30 days for eligible transactions. Merchant refunds may take 5-7 business days.",
                "steps": [
                    "Review refund eligibility (30-day window)",
                    "Check if transaction qualifies",
                    "Contact merchant if within policy"
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
            "message": "I can help you with refunds. Please provide more details about your refund request.",
            "steps": ["Provide transaction details", "Specify refund reason"],
            "reference": "",
            "can_resolve": True
        }

