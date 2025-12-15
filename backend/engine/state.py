from langgraph.graph import MessagesState

class AgentState(MessagesState):
    """The state of the agent for EcoCash Assistant with workflow tracking.
    
    Additional state fields (added dynamically):
    - current_workflow: Optional[str] - Current workflow name
    - workflow_step: Optional[str] - Current workflow step
    - transaction_context: Optional[Dict] - Transaction context
    - refund_context: Optional[Dict] - Refund context
    - loan_context: Optional[Dict] - Loan context
    - card_context: Optional[Dict] - Card context
    - issue_type: Optional[str] - Current issue type
    - resolution_attempted: bool - Whether resolution was attempted
    """
    pass
