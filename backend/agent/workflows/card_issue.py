"""Card issue workflow - handles card-related problems and enquiries."""

from typing import List, Dict, Any
from langchain_core.runnables import RunnableConfig
from engine.state import AgentState
from .base import BaseWorkflow


class CardIssueWorkflow(BaseWorkflow):
    """Workflow for card-related issues."""
    
    name = "card_issue"
    intent_keywords = [
        "card", "debit card", "credit card", "card blocked", "card not working",
        "card lost", "card stolen", "card declined", "card issue", "card problem"
    ]
    description = "Handle card-related issues and enquiries"
    
    async def summarize(self, state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
        """Get user's card information."""
        # In production, this would call a tool to get card details
        return {
            "cards": [
                {
                    "id": "card_1",
                    "type": "debit",
                    "last_four": "1234",
                    "status": "active",
                    "expiry": "12/26"
                }
            ],
            "user_id": state.get("user_id", "demo_user")
        }
    
    def get_summary_message(self, context: Dict[str, Any]) -> str:
        """Generate card summary message."""
        cards = context.get("cards", [])
        if cards:
            card = cards[0]
            return f"I can see you have a {card.get('type', 'card')} card ending in {card.get('last_four', '****')}. How can I help you with your card?"
        return "I can help you with card-related issues. What problem are you facing?"
    
    def get_question(self, context: Dict[str, Any]) -> str:
        """Get the question to ask after summary."""
        return "What issue are you experiencing with your card?"
    
    def get_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """Get common card issue suggestions."""
        return [
            "Card not working",
            "Card blocked",
            "Card declined",
            "Lost or stolen card",
            "Card activation",
            "Card limit increase"
        ]
    
    def get_resolution_guide(self, issue_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get resolution guidance for card issues."""
        cards = context.get("cards", [])
        card = cards[0] if cards else {}
        
        guides = {
            "card not working": {
                "message": "Let's troubleshoot your card. First, check if your card is activated and has sufficient balance.",
                "steps": [
                    "Verify card is activated",
                    "Check account balance",
                    "Try a different merchant or ATM",
                    "If still not working, we may need to block and reissue"
                ],
                "reference": card.get("id", ""),
                "can_resolve": True
            },
            "card blocked": {
                "message": "Your card may be blocked due to security reasons or suspicious activity. I can help you unblock it.",
                "steps": [
                    "Verify your identity",
                    "Confirm recent transactions",
                    "Unblock card if verified",
                    "If fraud suspected, card will remain blocked"
                ],
                "reference": card.get("id", ""),
                "can_resolve": False  # Requires security verification
            },
            "card declined": {
                "message": "Card declines can happen due to insufficient funds, merchant restrictions, or security checks.",
                "steps": [
                    "Check account balance",
                    "Verify transaction amount",
                    "Try a different merchant",
                    "Contact support if issue persists"
                ],
                "reference": card.get("id", ""),
                "can_resolve": True
            },
            "lost or stolen card": {
                "message": "If your card is lost or stolen, we need to block it immediately to prevent unauthorized use.",
                "steps": [
                    "Confirm card is lost/stolen",
                    "Block card immediately",
                    "Report to authorities if stolen",
                    "Request new card replacement"
                ],
                "reference": card.get("id", ""),
                "can_resolve": False  # Requires immediate action
            },
            "card activation": {
                "message": "I can help you activate your card. You'll need your card details and may need to set a PIN.",
                "steps": [
                    "Provide card number and CVV",
                    "Verify identity",
                    "Set PIN if required",
                    "Activate card"
                ],
                "reference": card.get("id", ""),
                "can_resolve": True
            },
            "card limit increase": {
                "message": "I can help you request a card limit increase. This requires a credit check and approval.",
                "steps": [
                    "Check current limit",
                    "Review eligibility for increase",
                    "Submit increase request",
                    "Wait for approval (usually 24-48 hours)"
                ],
                "reference": card.get("id", ""),
                "can_resolve": False  # Requires approval process
            }
        }
        
        issue_lower = issue_type.lower()
        for key, guide in guides.items():
            if key in issue_lower or issue_lower in key:
                return guide
        
        return {
            "message": "I can help you with card issues. Please describe the specific problem you're experiencing.",
            "steps": ["Describe the issue", "I'll provide specific guidance"],
            "reference": card.get("id", ""),
            "can_resolve": True
        }

