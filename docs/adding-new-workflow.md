# How to Add a New Workflow (LangGraph Subgraph Approach)

This guide shows you how to add a new guided support workflow using LangGraph subgraphs.

## Overview

Each workflow is a LangGraph subgraph that:
1. Detects user intent
2. Summarizes relevant context
3. Returns control to `chat_node` for guidance

**Guidance logic lives in `chat_node` via system message**, not in subgraphs.

## Step-by-Step Guide

### Step 1: Create Subgraph File

Create a new file in `backend/agent/workflows/subgraphs/`, e.g., `insurance_graph.py`:

```python
"""Insurance workflow as LangGraph subgraph."""

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from engine.state import AgentState
from copilotkit.langgraph import copilotkit_emit_message
import logging

logger = logging.getLogger(__name__)


async def summarize_insurance_node(state: AgentState, config: RunnableConfig):
    """Step 1: Get insurance information and summarize."""
    logger.debug("Insurance subgraph: Starting summarization")
    
    # Call tools or fetch data (placeholder example)
    # In production, call insurance tools here
    state["insurance_context"] = {
        "policies": [
            {
                "id": "policy_1",
                "type": "health",
                "status": "active",
                "premium": 500.0
            }
        ]
    }
    state["current_workflow"] = "insurance"
    state["workflow_step"] = "summarized"
    
    # Create summary message
    policies = state["insurance_context"].get("policies", [])
    if policies:
        summary_msg = f"You have {len(policies)} active insurance policy(ies). How can I help you with insurance?"
    else:
        summary_msg = "I can help you with insurance enquiries and claims. What would you like to know?"
    
    state["messages"].append(AIMessage(content=summary_msg))
    await copilotkit_emit_message(config, summary_msg)
    
    # Mark workflow as completed and clear current_workflow
    state["workflow_step"] = "completed"
    state["current_workflow"] = None
    
    logger.debug("Insurance subgraph: Summarization complete, returning to main graph")
    
    return state


def build_insurance_subgraph():
    """Build and compile the insurance subgraph."""
    graph = StateGraph(AgentState)
    graph.add_node("summarize", summarize_insurance_node)
    graph.add_edge(START, "summarize")
    graph.add_edge("summarize", END)
    return graph.compile()
```

### Step 2: Register Intent Detection

Update `backend/agent/workflows/subgraphs/__init__.py`:

```python
# Add import
from .insurance_graph import build_insurance_subgraph

# Update detect_workflow_intent function
def detect_workflow_intent(user_message: str) -> Optional[str]:
    user_lower = user_message.lower()
    
    # Priority order: most specific first
    if any(kw in user_lower for kw in ["help with transaction", "transaction issue"]):
        return "transaction_help"
    elif any(kw in user_lower for kw in ["insurance", "claim", "coverage", "policy"]):
        return "insurance"  # Add your workflow
    # ... existing workflows
    
    return None

# Update get_workflow_subgraph function
def get_workflow_subgraph(workflow_name: str) -> Optional[...]:
    if workflow_name == "insurance":
        return build_insurance_subgraph()
    # ... existing workflows
    return None
```

### Step 3: Add to Main Graph

Update `backend/agent/graph.py`:

```python
# Add import
from agent.workflows.subgraphs.insurance_graph import build_insurance_subgraph

# Add subgraph as node
graph_builder.add_node("insurance", build_insurance_subgraph())

# Add edge after subgraph
graph_builder.add_edge("insurance", "chat_node")

# Update route_after_intent to include new workflow
graph_builder.add_conditional_edges(
    "detect_intent",
    route_after_intent,
    {
        "transaction_help": "transaction_help",
        "insurance": "insurance",  # Add here
        # ... existing workflows
        "chat_node": "chat_node"
    }
)
```

### Step 4: Add Guidance to chat_node (Optional)

If your workflow needs specific guidance, update `backend/engine/chat.py` system message:

```python
system_message = """
...
INSURANCE WORKFLOW:
When user asks about insurance:
- Provide information about their policies
- Guide them through claim filing if needed
- Only escalate to ticket for complex cases
...
"""
```

### Step 5: Add Tools (if needed)

If your workflow needs new tools, add them to `backend/agent/tools.py`:

```python
@tool
def get_insurance_policies(user_id: str) -> Dict:
    """Get user's insurance policies."""
    # Implementation
    pass

@tool
def file_insurance_claim(user_id: str, claim_details: Dict) -> str:
    """File an insurance claim."""
    # Implementation
    pass
```

Then add tools to `ToolNode` in `graph.py` and bind to LLM in `chat.py`.

## Workflow Pattern

Every workflow subgraph follows this pattern:

```
START → summarize_node → END
         ↓
    - Fetch context
    - Update state with workflow_context
    - Set current_workflow and workflow_step
    - Emit summary message
    - Clear current_workflow (set to None)
    - Set workflow_step = "completed"
    - Return to main graph → chat_node
```

## State Management

### Required State Updates

```python
# In summarize_node:
state["insurance_context"] = {...}  # Workflow-specific context
state["current_workflow"] = "insurance"
state["workflow_step"] = "summarized"

# After summarization:
state["workflow_step"] = "completed"
state["current_workflow"] = None  # CRITICAL: Clear to allow new intents
```

### Accessing Context in chat_node

The workflow context persists in state, so `chat_node` can access it:

```python
# In chat_node system message or logic:
transaction_context = state.get("transaction_context")
insurance_context = state.get("insurance_context")
# Use context to provide personalized guidance
```

## Best Practices

1. **Keep Subgraphs Simple**: Focus on summarization only
2. **Clear Workflow State**: Always clear `current_workflow` after completion
3. **Add Logging**: Use `logger.debug()` for entry/exit, `logger.info()` for important events
4. **Error Handling**: Wrap tool calls in try/except with fallbacks
5. **State Context**: Store workflow-specific data in `{workflow}_context` field
6. **Guidance in chat_node**: Don't put guidance logic in subgraphs; use system message

## Testing

1. **Test Subgraph Independently**:
```python
from agent.workflows.subgraphs.insurance_graph import build_insurance_subgraph
graph = build_insurance_subgraph()
result = await graph.ainvoke({
    "messages": [HumanMessage(content="I need help with insurance")],
    "user_id": "demo_user"
})
```

2. **Test in Main Graph**:
- Send message matching intent keywords
- Verify routing to subgraph
- Check state updates
- Verify message flow
- Confirm `current_workflow` is cleared

3. **Test Intent Detection**:
```python
from agent.workflows.subgraphs import detect_workflow_intent
assert detect_workflow_intent("I need insurance help") == "insurance"
```

## Troubleshooting

### Subgraph Not Routing
- Check `detect_workflow_intent` includes your keywords
- Verify keywords are specific enough (not matching other workflows)
- Check `route_after_intent` returns correct workflow name
- Ensure subgraph is added to main graph

### State Not Clearing
- Verify `current_workflow = None` is set after completion
- Check `workflow_step = "completed"` is set
- Ensure state dict is returned from node

### Import Errors
- **`CompiledGraph` import error**: LangGraph doesn't export this. Just use `.compile()` directly, no type annotation needed.
- Ensure all imports are correct
- Check subgraph file is in correct directory

## Example: Complete Workflow

See `backend/agent/workflows/subgraphs/transaction_help_graph.py` for a complete example with:
- Tool calls
- State management
- Logging
- Error handling
- Message emission

## Checklist

- [ ] Subgraph file created in `subgraphs/` directory
- [ ] Intent detection added to `__init__.py`
- [ ] Subgraph added to main graph
- [ ] Edge added from subgraph to `chat_node`
- [ ] State cleared after completion (`current_workflow = None`)
- [ ] Logging added for debugging
- [ ] Tools added (if needed)
- [ ] Guidance added to `chat_node` system message (if needed)
- [ ] Tested independently
- [ ] Tested in main graph
- [ ] Intent detection tested
