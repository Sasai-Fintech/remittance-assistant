"""Base workflow class for guided support flows.

All workflows should inherit from this class and implement the required methods.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from langchain_core.runnables import RunnableConfig
from engine.state import AgentState


class BaseWorkflow(ABC):
    """Base class for all support workflows."""
    
    # Override in subclasses
    name: str = ""  # Unique workflow identifier
    intent_keywords: List[str] = []  # Keywords that trigger this workflow
    description: str = ""  # Human-readable description
    
    @classmethod
    def matches_intent(cls, user_message: str) -> bool:
        """Check if user message matches this workflow's intent."""
        user_lower = user_message.lower()
        return any(keyword in user_lower for keyword in cls.intent_keywords)
    
    @abstractmethod
    async def summarize(self, state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Step 1: Get relevant context and summarize.
        Returns a dict with context information (transaction details, loan status, etc.)
        """
        pass
    
    @abstractmethod
    def get_summary_message(self, context: Dict[str, Any]) -> str:
        """
        Step 2: Generate the summary message shown to user.
        Example: "Good news: your payment of $50.00 to Coffee Shop was successful."
        """
        pass
    
    @abstractmethod
    def get_question(self, context: Dict[str, Any]) -> str:
        """
        Step 3: Get the question to ask after summary.
        Example: "Tell us what's wrong" or "What would you like to know?"
        """
        pass
    
    @abstractmethod
    def get_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """
        Step 4: Get common issue suggestions.
        Returns list of suggestion strings.
        """
        pass
    
    @abstractmethod
    def get_resolution_guide(self, issue_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 5: Get resolution guidance for a specific issue.
        Returns dict with:
        - message: Guidance text
        - steps: List of actionable steps
        - reference: Reference number/ID if applicable
        - can_resolve: Whether this can be resolved without ticket
        """
        pass
    
    def should_escalate(self, user_message: str, context: Dict[str, Any]) -> bool:
        """
        Step 6: Determine if issue should be escalated to ticket.
        Override if custom escalation logic needed.
        """
        escalate_keywords = [
            "create ticket", "raise ticket", "escalate", "not resolved",
            "contacted merchant, issue not resolved", "still having problem"
        ]
        user_lower = user_message.lower()
        return any(keyword in user_lower for keyword in escalate_keywords)
    
    def get_ticket_subject(self, issue_type: str, context: Dict[str, Any]) -> str:
        """Generate ticket subject from issue and context."""
        return f"{issue_type} - {self.name.title()} Support Request"
    
    def get_ticket_body(self, issue_type: str, context: Dict[str, Any], conversation_history: List[str]) -> str:
        """Generate ticket body from issue, context, and conversation."""
        body = f"Issue Type: {issue_type}\n"
        body += f"Workflow: {self.name}\n\n"
        body += f"Context: {context}\n\n"
        body += f"Conversation Summary:\n" + "\n".join(conversation_history[-3:])
        return body

