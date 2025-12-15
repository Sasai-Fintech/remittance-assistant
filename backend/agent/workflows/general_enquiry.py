"""General enquiry workflow - handles miscellaneous questions."""

from typing import List, Dict, Any
from langchain_core.runnables import RunnableConfig
from engine.state import AgentState
from .base import BaseWorkflow


class GeneralEnquiryWorkflow(BaseWorkflow):
    """Workflow for general enquiries that don't fit other categories."""
    
    name = "general_enquiry"
    intent_keywords = [
        "help", "question", "enquiry", "information", "how to",
        "what is", "tell me about", "explain", "guide"
    ]
    description = "Handle general enquiries and questions"
    
    async def summarize(self, state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
        """Get general context about user's account."""
        return {
            "user_id": state.get("user_id", "demo_user"),
            "account_status": "active"
        }
    
    def get_summary_message(self, context: Dict[str, Any]) -> str:
        """Generate general enquiry greeting."""
        return "I'm here to help! What would you like to know?"
    
    def get_question(self, context: Dict[str, Any]) -> str:
        """Get the question to ask after summary."""
        return "How can I assist you today?"
    
    def get_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """Get common general enquiry suggestions."""
        return [
            "Account information",
            "How to use features",
            "Fees and charges",
            "Security tips",
            "Contact support"
        ]
    
    def get_resolution_guide(self, issue_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get resolution guidance for general enquiries."""
        guides = {
            "account information": {
                "message": "I can help you with account information. What specific details do you need?",
                "steps": [
                    "Specify what information you need",
                    "I'll provide the details",
                    "If sensitive, I'll guide you to secure channels"
                ],
                "reference": "",
                "can_resolve": True
            },
            "how to use features": {
                "message": "I can guide you through our features. Which feature would you like to learn about?",
                "steps": [
                    "Specify the feature",
                    "I'll provide step-by-step guide",
                    "Answer any follow-up questions"
                ],
                "reference": "",
                "can_resolve": True
            },
            "fees and charges": {
                "message": "I can explain our fees and charges. Which service are you asking about?",
                "steps": [
                    "Specify the service",
                    "I'll provide fee structure",
                    "Explain when charges apply"
                ],
                "reference": "",
                "can_resolve": True
            },
            "security tips": {
                "message": "Security is important! Here are some tips: Never share your PIN, enable 2FA, monitor transactions regularly.",
                "steps": [
                    "Review security best practices",
                    "Enable security features",
                    "Set up transaction alerts"
                ],
                "reference": "",
                "can_resolve": True
            },
            "contact support": {
                "message": "I can help you contact support. For urgent issues, you can create a support ticket or call our helpline.",
                "steps": [
                    "Describe your issue",
                    "I'll determine best support channel",
                    "Connect you with appropriate support"
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
            "message": "I'm here to help! Please tell me more about what you need.",
            "steps": ["Describe your enquiry", "I'll provide information or guidance"],
            "reference": "",
            "can_resolve": True
        }

