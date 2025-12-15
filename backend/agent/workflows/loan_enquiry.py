"""Loan enquiry workflow - handles loan-related questions and applications."""

from typing import List, Dict, Any
from langchain_core.runnables import RunnableConfig
from engine.state import AgentState
from .base import BaseWorkflow


class LoanEnquiryWorkflow(BaseWorkflow):
    """Workflow for loan enquiries and applications."""
    
    name = "loan_enquiry"
    intent_keywords = [
        "loan", "borrow", "credit", "apply for loan", "loan application",
        "loan status", "loan repayment", "loan interest", "loan eligibility"
    ]
    description = "Handle loan enquiries, applications, and status checks"
    
    async def summarize(self, state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
        """Get user's loan information."""
        # In production, this would call a tool to get loan details
        return {
            "active_loans": [],
            "loan_eligibility": {
                "eligible": True,
                "max_amount": 50000,
                "interest_rate": 12.5
            },
            "user_id": state.get("user_id", "demo_user")
        }
    
    def get_summary_message(self, context: Dict[str, Any]) -> str:
        """Generate loan summary message."""
        active_loans = context.get("active_loans", [])
        if active_loans:
            return f"You have {len(active_loans)} active loan(s). How can I help you with your loan?"
        return "I can help you with loan enquiries, applications, and managing your existing loans."
    
    def get_question(self, context: Dict[str, Any]) -> str:
        """Get the question to ask after summary."""
        return "What would you like to know about loans?"
    
    def get_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """Get common loan-related suggestions."""
        return [
            "Apply for a loan",
            "Check loan eligibility",
            "Loan interest rates",
            "Loan repayment schedule",
            "Early repayment options"
        ]
    
    def get_resolution_guide(self, issue_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get resolution guidance for loan enquiries."""
        eligibility = context.get("loan_eligibility", {})
        
        guides = {
            "apply for a loan": {
                "message": f"Great! You're eligible for loans up to {eligibility.get('max_amount', 0):,}. Current interest rate: {eligibility.get('interest_rate', 0)}% APR.",
                "steps": [
                    "Review loan terms and interest rates",
                    "Choose loan amount and tenure",
                    "Complete application form",
                    "Submit required documents"
                ],
                "reference": "",
                "can_resolve": False  # Requires application process
            },
            "check loan eligibility": {
                "message": f"Based on your account, you're eligible for loans up to {eligibility.get('max_amount', 0):,} with {eligibility.get('interest_rate', 0)}% APR.",
                "steps": [
                    "Review eligibility criteria",
                    "Check maximum loan amount",
                    "Review interest rates",
                    "Start application if interested"
                ],
                "reference": "",
                "can_resolve": True
            },
            "loan interest rates": {
                "message": f"Our current loan interest rates start at {eligibility.get('interest_rate', 0)}% APR. Rates vary based on loan amount, tenure, and credit profile.",
                "steps": [
                    "Review interest rate structure",
                    "Calculate total interest for your loan amount",
                    "Compare with other options",
                    "Apply if rates are acceptable"
                ],
                "reference": "",
                "can_resolve": True
            },
            "loan repayment schedule": {
                "message": "I can show you your loan repayment schedule. Please provide your loan account number or I can check your active loans.",
                "steps": [
                    "Provide loan account number",
                    "I'll fetch your repayment schedule",
                    "Review upcoming payments and dates"
                ],
                "reference": "",
                "can_resolve": True
            },
            "early repayment options": {
                "message": "You can make early repayments to reduce interest. There may be a small processing fee. I can help you calculate savings.",
                "steps": [
                    "Review early repayment terms",
                    "Calculate interest savings",
                    "Check processing fees",
                    "Initiate early repayment if desired"
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
            "message": "I can help you with loan-related questions. What specific information do you need?",
            "steps": ["Specify your loan enquiry", "I'll provide detailed information"],
            "reference": "",
            "can_resolve": True
        }

