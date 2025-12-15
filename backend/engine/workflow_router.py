"""Workflow router - routes user messages to appropriate workflows."""

from typing import Optional, Dict, Any
from langchain_core.runnables import RunnableConfig
from engine.state import AgentState
from agent.workflows import detect_workflow, get_workflow


async def route_to_workflow(state: AgentState, config: RunnableConfig) -> Optional[Dict[str, Any]]:
    """
    Route user message to appropriate workflow.
    Returns workflow context if a workflow is detected, None otherwise.
    """
    messages = state.get("messages", [])
    if not messages:
        return None
    
    # Get the last user message
    last_message = messages[-1]
    user_message = str(last_message.content) if hasattr(last_message, 'content') else ""
    
    if not user_message:
        return None
    
    # Detect which workflow to use
    workflow_name = detect_workflow(user_message)
    if not workflow_name:
        return None
    
    # Get workflow class
    workflow_class = get_workflow(workflow_name)
    if not workflow_class:
        return None
    
    # Create workflow instance and get context
    workflow = workflow_class()
    context = await workflow.summarize(state, config)
    
    return {
        "workflow_name": workflow_name,
        "workflow": workflow,
        "context": context,
        "user_message": user_message
    }


def get_workflow_instructions(workflow_context: Dict[str, Any]) -> str:
    """
    Generate system instructions for the detected workflow.
    This helps the LLM understand how to handle the conversation.
    """
    workflow = workflow_context.get("workflow")
    context = workflow_context.get("context", {})
    
    if not workflow:
        return ""
    
    # Get workflow-specific instructions
    summary_msg = workflow.get_summary_message(context)
    question = workflow.get_question(context)
    suggestions = workflow.get_suggestions(context)
    
    instructions = f"""
    WORKFLOW DETECTED: {workflow.name} - {workflow.description}
    
    STEP 1: Provide the summary message to the user:
    "{summary_msg}"
    
    STEP 2: Ask the question:
    "{question}"
    
    STEP 3: Wait for user to respond. Common responses they might give:
    {', '.join(f'"{s}"' for s in suggestions)}
    
    STEP 4: When user describes their issue, call the workflow's get_resolution_guide method
    to get specific guidance. Provide empathetic, actionable steps.
    
    STEP 5: Only escalate to create_ticket if:
    - User explicitly requests ticket creation
    - User confirms they've tried suggested solutions and issue persists
    - Issue requires escalation (security, fraud, complex technical issues)
    
    Be empathetic and helpful. Guide users through self-service options first.
    """
    
    return instructions

