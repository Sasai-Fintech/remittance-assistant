from langchain_core.tools import tool
from typing import Optional, List, Dict

@tool
def get_balance(user_id: str) -> Dict[str, float]:
    """Get the current balance for a user."""
    # Dummy data
    return {
        "USD": 1500.00,
        "ZIG": 5000.00
    }

@tool
def list_transactions(user_id: str, limit: int = 5) -> List[Dict]:
    """List recent transactions for a user."""
    # Dummy data
    return [
        {"id": "txn_1", "amount": 50.00, "currency": "USD", "merchant": "Netflix", "date": "2023-10-25"},
        {"id": "txn_2", "amount": 12.50, "currency": "USD", "merchant": "Uber", "date": "2023-10-24"},
        {"id": "txn_3", "amount": 100.00, "currency": "ZIG", "merchant": "Airtime", "date": "2023-10-23"},
    ]

@tool
def create_ticket(user_id: str, issue: str, description: str) -> str:
    """Create a support ticket."""
    # Dummy logic
    return f"Ticket created successfully. ID: TICKET-{hash(issue) % 10000}"

@tool
def get_ticket_status(ticket_id: str) -> str:
    """Get the status of a support ticket."""
    return "In Progress"

@tool
def show_balance_widget(accounts: List[Dict]) -> str:
    """Show the balance card widget to the user.
    accounts: List of dicts with id, label, balance (currency, amount).
    """
    return "Balance widget displayed."

@tool
def show_transactions_widget(transactions: List[Dict]) -> str:
    """Show the transactions table widget to the user.
    transactions: List of dicts with id, date, merchant, amount, currency.
    """
    return "Transactions widget displayed."

@tool
def request_ticket_confirmation(issue: str, description: str) -> str:
    """Request confirmation from the user to create a ticket.
    Returns the user's decision (Confirmed/Cancelled).
    """
    return "Waiting for user confirmation..."

ALL_TOOLS = [get_balance, list_transactions, create_ticket, get_ticket_status, show_balance_widget, show_transactions_widget, request_ticket_confirmation]
