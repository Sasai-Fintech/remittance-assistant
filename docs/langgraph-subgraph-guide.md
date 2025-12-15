# LangGraph Subgraph Workflow Guide

## Overview

This guide explains how to create and use LangGraph subgraphs for support workflows. Subgraphs provide native state management, visual debugging, and better scalability than class-based workflows.

## Architecture

### Main Graph Structure

```
START → detect_intent → [workflow subgraph] → chat_node → [tools/tickets] → END
```

The main graph routes to workflow subgraphs based on user intent, then continues to chat_node for LLM processing.

### Subgraph Structure

Each workflow subgraph follows this pattern:

```
START → summarize_node → END
```

After summarization, the subgraph returns to the main graph, which routes to `chat_node` for continued conversation.

## Creating a New Workflow Subgraph

### Step 1: Create Subgraph File

Create a new file in `backend/agent/workflows/subgraphs/`:

```python
# backend/agent/workflows/subgraphs/my_workflow_graph.py
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from engine.state import AgentState
from copilotkit.langgraph import copilotkit_emit_message

async def summarize_workflow_node(state: AgentState, config: RunnableConfig):
    """Step 1: Get context and summarize."""
    import logging
    logger = logging.getLogger(__name__)
    logger.debug("My workflow subgraph: Starting summarization")
    
    # Get relevant data (call tools, fetch from state, etc.)
    context_data = {...}
    
    # Update state
    state["my_workflow_context"] = context_data
    state["current_workflow"] = "my_workflow"
    state["workflow_step"] = "summarized"
    
    # Create summary message
    summary_msg = "Your summary message here..."
    
    # Add message to state
    state["messages"].append(AIMessage(content=summary_msg))
    await copilotkit_emit_message(config, summary_msg)
    
    # Mark workflow as completed and clear current_workflow to allow new intent detection
    state["workflow_step"] = "completed"
    state["current_workflow"] = None
    
    logger.debug("My workflow subgraph: Summarization complete, returning to main graph")
    
    return state

def build_my_workflow_subgraph():
    """Build and compile the workflow subgraph."""
    graph = StateGraph(AgentState)
    graph.add_node("summarize", summarize_workflow_node)
    graph.add_edge(START, "summarize")
    graph.add_edge("summarize", END)
    return graph.compile()
```

### Step 2: Register in `__init__.py`

Update `backend/agent/workflows/subgraphs/__init__.py`:

```python
from .my_workflow_graph import build_my_workflow_subgraph

# Add to detect_workflow_intent function
def detect_workflow_intent(user_message: str) -> Optional[str]:
    user_lower = user_message.lower()
    if any(kw in user_lower for kw in ["my keyword", "another keyword"]):
        return "my_workflow"
    # ... existing workflows
```

### Step 3: Add to Main Graph

Update `backend/agent/graph.py`:

```python
from agent.workflows.subgraphs.my_workflow_graph import build_my_workflow_subgraph

# Add subgraph as node
graph_builder.add_node("my_workflow", build_my_workflow_subgraph())

# Add edge after subgraph
graph_builder.add_edge("my_workflow", "chat_node")

# Update route_after_intent to include new workflow
def route_after_intent(state: AgentState):
    current_workflow = state.get("current_workflow")
    if current_workflow == "my_workflow":
        return "my_workflow"
    # ... existing routing
```

## State Management

### Adding State Fields

State fields are added dynamically to the state dict. No need to modify `AgentState` class:

```python
# In your subgraph node
state["current_workflow"] = "my_workflow"
state["workflow_step"] = "summarized"
state["my_context"] = {...}

# IMPORTANT: Clear current_workflow after completion to allow new workflows
state["workflow_step"] = "completed"
state["current_workflow"] = None
```

### State Lifecycle

1. **Intent Detection**: `detect_intent_node` sets `current_workflow` based on user message
2. **Subgraph Execution**: Subgraph updates workflow-specific context and sets `workflow_step`
3. **Completion**: Subgraph clears `current_workflow` and sets `workflow_step = "completed"`
4. **Return to Chat**: Main graph routes to `chat_node` for continued conversation
5. **New Intent**: After `current_workflow` is cleared, new intents can be detected

### Accessing State in Nodes

```python
async def my_node(state: AgentState, config: RunnableConfig):
    workflow = state.get("current_workflow")
    context = state.get("my_context", {})
    # Use state data
    return state
```

## Tool Integration

### Calling Tools from Subgraphs

Tools can be called directly or through ToolNode:

```python
from agent.tools import my_tool

# Direct call (simple cases)
result = my_tool.invoke({"param": "value"})

# Through ToolNode (for proper graph integration)
tool_node = ToolNode([my_tool])
# Create AIMessage with tool_call
# Invoke tool_node
```

## CopilotKit Integration

### Widget Rendering

Widgets are automatically rendered when tools are called. No changes needed to frontend:

- Tool names must match frontend widget registrations
- Tool return values are passed to widget `render` functions
- Status tracking works automatically

### Message Emission

Use `copilotkit_emit_message` to send messages to frontend:

```python
from copilotkit.langgraph import copilotkit_emit_message

await copilotkit_emit_message(config, "Your message here")
```

## Benefits of Subgraphs

1. **Native State Management**: State persists across workflow steps with checkpointing
2. **Visual Debugging**: View workflow execution in LangGraph Studio
3. **Better Error Handling**: LangGraph handles errors and recovery
4. **Flexible Routing**: Conditional edges based on state
5. **Interrupts**: Human-in-the-loop at any step
6. **Scalability**: Easy to add new workflows without touching existing code

## Example: Complete Workflow

See `backend/agent/workflows/subgraphs/transaction_help_graph.py` for a complete example with:
- Tool calls
- State management
- Message emission
- Multiple nodes

## Testing

1. Test subgraph independently:
```python
from agent.workflows.subgraphs.my_workflow_graph import build_my_workflow_subgraph
graph = build_my_workflow_subgraph()
result = await graph.ainvoke(initial_state)
```

2. Test in main graph:
- Send message matching workflow intent
- Verify routing to subgraph
- Check state updates
- Verify message flow

## Migration from Class-Based Workflows

If migrating from class-based workflows:

1. Convert `summarize()` method → `summarize_node()` function
2. Convert `get_summary_message()` → inline in node
3. Move guidance logic to `chat_node` or separate node
4. Update state management to use state dict directly
5. Register in subgraphs `__init__.py` and main graph

## Best Practices

1. **Keep Subgraphs Simple**: Focus on summarization, let `chat_node` handle guidance via system message
2. **Clear Workflow State**: Always clear `current_workflow` after subgraph completes to allow new intent detection
3. **Use State Dict**: Add fields dynamically, don't modify AgentState class
4. **Emit Messages**: Always use `copilotkit_emit_message` for user-facing messages
5. **Tool Integration**: Call tools directly for simple cases, use ToolNode for complex flows
6. **Error Handling**: Wrap tool calls in try/except with logging and fallbacks
7. **State Persistence**: State fields persist automatically with checkpointing
8. **Add Logging**: Use `logging.getLogger(__name__)` for debug/info/error logging

## Troubleshooting

### Subgraph Not Routing
- Check `detect_workflow_intent` includes your keywords
- Verify `route_after_intent` returns correct workflow name
- Ensure subgraph is added to main graph
- Check logs for intent detection messages

### State Not Persisting
- Verify checkpointer is enabled in `build_graph()`
- Check state fields are set correctly
- Ensure state dict is returned from nodes
- Verify `current_workflow` is cleared after completion

### Tools Not Working
- Verify tool names match frontend widgets
- Check tool is imported and bound to LLM
- Ensure ToolNode includes your tool
- Check logs for tool invocation errors

### Messages Not Appearing
- Use `copilotkit_emit_message` for all user messages
- Check message is added to state["messages"]
- Verify frontend is connected to backend

### CopilotKit Suggestions Not Loading
- Verify `/api/copilotkit/info` endpoint returns 200 (not 500)
- Check backend logs for import errors (e.g., `CompiledGraph` import issues)
- Ensure graph compiles successfully: `python -c "from agent.graph import build_graph; build_graph()"`
- Restart backend after graph changes

### Import Errors
- **`CompiledGraph` import error**: LangGraph doesn't export `CompiledGraph`. Subgraphs are just compiled graph objects returned by `.compile()`. Remove any `from langgraph.graph import CompiledGraph` imports.
- Use `StateGraph(...).compile()` directly, no type annotation needed

