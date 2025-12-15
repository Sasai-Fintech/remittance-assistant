"""Transaction help workflow - refactored from existing implementation."""

from typing import List, Dict, Any
from langchain_core.runnables import RunnableConfig
from engine.state import AgentState
from .base import BaseWorkflow
from agent.tools import get_transaction_details


class TransactionHelpWorkflow(BaseWorkflow):
    """Workflow for helping users with transaction issues."""
    
    name = "transaction_help"
    intent_keywords = [
        "help with transaction", "transaction issue", "payment problem",
        "transaction to", "payment to", "help with my transaction"
    ]
    description = "Help users resolve transaction-related issues"
    
    async def summarize(self, state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
        """Get transaction details."""
        # Extract transaction_id from conversation if available
        messages = state.get("messages", [])
        transaction_id = ""
        
        # Try to extract transaction ID from recent messages
        for msg in reversed(messages[-5:]):  # Check last 5 messages
            content = str(msg.content).lower()
            if "txn_" in content:
                # Extract transaction ID (simplified - in production, use better parsing)
                import re
                match = re.search(r'txn_\d+', content)
                if match:
                    transaction_id = match.group(0)
                    break
        
        # In production, the tool would be called through the graph
        # For now, we'll call it directly (this should be refactored to use graph tools)
        # The workflow router will handle tool calls through the graph
        try:
            result = get_transaction_details.invoke({
                "user_id": state.get("user_id", "demo_user"),
                "transaction_id": transaction_id
            })
        except Exception:
            # Fallback to mock data if tool call fails
            from datetime import datetime, timedelta
            result = {
                "id": "txn_1",
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "merchant": "Coffee Shop",
                "description": "Coffee",
                "amount": -50.0,
                "currency": "USD",
                "status": "completed",
                "reference": "532300764753"
            }
        
        return {
            "transaction": result,
            "transaction_id": result.get("id", ""),
            "merchant": result.get("merchant", ""),
            "date": result.get("date", ""),
            "amount": result.get("amount", 0),
            "currency": result.get("currency", "USD"),
            "reference": result.get("reference", ""),
            "status": result.get("status", "completed")
        }
    
    def get_summary_message(self, context: Dict[str, Any]) -> str:
        """Generate transaction summary message."""
        transaction = context.get("transaction", {})
        amount = abs(transaction.get("amount", 0))
        currency = transaction.get("currency", "USD")
        merchant = transaction.get("merchant", "merchant")
        date = transaction.get("date", "")
        
        # Format date
        from datetime import datetime
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d %b %Y")
        except:
            formatted_date = date
        
        return f"Good news: your payment of {amount:.2f} {currency} to {merchant} on {formatted_date} was successful."
    
    def get_question(self, context: Dict[str, Any]) -> str:
        """Get the question to ask after summary."""
        return "Tell us what's wrong"
    
    def get_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """Get common transaction issue suggestions."""
        return [
            "Receiver has not received the payment",
            "Amount debited twice",
            "Transaction failed",
            "Need refund",
            "Wrong amount charged",
            "Offer not applied"
        ]
    
    def get_resolution_guide(self, issue_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get resolution guidance for transaction issues."""
        transaction = context.get("transaction", {})
        merchant = transaction.get("merchant", "the merchant")
        reference = transaction.get("reference", "")
        
        guides = {
            "receiver has not received the payment": {
                "message": f"We hate it when that happens too. Here's what you can do: contact {merchant} with UTR: {reference}. Only the merchant can initiate refunds.",
                "steps": [
                    f"Contact {merchant} directly",
                    f"Provide them with UTR: {reference}",
                    "Request payment confirmation or refund"
                ],
                "reference": reference,
                "can_resolve": True
            },
            "amount debited twice": {
                "message": f"Check if one transaction is still pending. If both are completed, contact {merchant} with UTR: {reference}.",
                "steps": [
                    "Check your transaction history for duplicate entries",
                    "Verify if one is still pending (will auto-reverse)",
                    f"If both completed, contact {merchant} with UTR: {reference}"
                ],
                "reference": reference,
                "can_resolve": True
            },
            "transaction failed": {
                "message": f"This usually auto-reverses in 24-48 hours. If not, contact {merchant} with UTR: {reference}.",
                "steps": [
                    "Wait 24-48 hours for automatic reversal",
                    f"If not reversed, contact {merchant} with UTR: {reference}",
                    "Provide transaction details for investigation"
                ],
                "reference": reference,
                "can_resolve": True
            },
            "need refund": {
                "message": f"Contact {merchant} directly with UTR: {reference} to request refund.",
                "steps": [
                    f"Contact {merchant} customer support",
                    f"Provide UTR: {reference}",
                    "Request refund with reason"
                ],
                "reference": reference,
                "can_resolve": True
            },
            "wrong amount charged": {
                "message": f"Contact {merchant} with UTR: {reference} to dispute the charge.",
                "steps": [
                    f"Contact {merchant} billing department",
                    f"Provide UTR: {reference} and correct amount",
                    "Request charge correction"
                ],
                "reference": reference,
                "can_resolve": True
            },
            "offer not applied": {
                "message": f"Contact {merchant} or check offer terms. UTR: {reference}",
                "steps": [
                    "Review offer terms and conditions",
                    f"Contact {merchant} with UTR: {reference}",
                    "Verify eligibility and request credit"
                ],
                "reference": reference,
                "can_resolve": True
            }
        }
        
        # Find matching guide (case-insensitive)
        issue_lower = issue_type.lower()
        for key, guide in guides.items():
            if key in issue_lower or issue_lower in key:
                return guide
        
        # Default guide
        return {
            "message": f"Contact {merchant} with UTR: {reference} for assistance.",
            "steps": [f"Contact {merchant} customer support", f"Provide UTR: {reference}"],
            "reference": reference,
            "can_resolve": True
        }

