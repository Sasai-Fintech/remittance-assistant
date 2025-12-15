# Scaling Architecture for Multiple Workflows

## Overview

This document outlines a scalable architecture to handle multiple guided support workflows (refunds, loans, cards, general enquiries, etc.) using **LangGraph subgraphs** for native state management and better scalability.

## Architecture Principles

1. **LangGraph Subgraphs**: Each workflow is a compiled LangGraph subgraph
2. **Native State Management**: State persists across workflow steps with checkpointing
3. **Visual Debugging**: View workflow execution in LangGraph Studio
4. **Modular Design**: Each workflow is self-contained in its own subgraph
5. **Tool Integration**: Tools accessible from any subgraph node
6. **Conditional Routing**: Main graph routes to appropriate subgraph based on intent

## Directory Structure

```
backend/
├── agent/
│   ├── tools.py                  # All tools (get_balance, list_transactions, create_ticket, etc.)
│   ├── workflows/
│   │   ├── subgraphs/
│   │   │   ├── __init__.py           # Subgraph registry and intent detection
│   │   │   ├── transaction_help_graph.py  # Transaction help subgraph
│   │   │   ├── refund_graph.py       # Refund subgraph
│   │   │   ├── loan_enquiry_graph.py # Loan enquiry subgraph
│   │   │   ├── card_issue_graph.py   # Card issue subgraph
│   │   │   ├── general_enquiry_graph.py # General enquiry subgraph
│   │   │   └── shared_nodes.py       # Shared nodes (if any)
│   │   └── __init__.py
│   ├── graph.py                 # Main graph (routes to subgraphs)
│   └── state.py                 # State definitions (in engine/)
├── engine/
│   ├── chat.py                  # Chat node (LLM processing)
│   └── state.py                # AgentState definition
```

## Workflow Pattern

Every workflow follows this pattern:

```
1. DETECT INTENT → detect_intent_node identifies workflow from user message
2. ROUTE TO SUBGRAPH → Main graph routes to appropriate subgraph
3. SUMMARIZE → Subgraph gets context and provides summary message
4. RETURN TO CHAT → Subgraph completes, clears current_workflow, returns to chat_node
5. GUIDANCE → chat_node provides guidance based on system message and context
6. ESCALATE → Create ticket only if needed (via create_ticket tool)
```

**Key Points:**
- Subgraphs focus on summarization only
- Guidance logic lives in `chat_node` via system message
- Subgraphs clear `current_workflow` after completion to allow new intents
- State context (e.g., `transaction_context`) persists for `chat_node` to use

## Implementation Plan

### Phase 1: Base Infrastructure
- Create base workflow class
- Create workflow registry
- Refactor existing transaction workflow to use base class

### Phase 2: Add New Workflows
- Refund workflow
- Loan enquiry workflow
- Card issue workflow
- General enquiry workflow

### Phase 3: Advanced Features
- Workflow state persistence
- Workflow analytics
- A/B testing different workflows
- Multi-step workflows with branching

## Example: Adding a New Workflow

See `ADDING_NEW_WORKFLOW.md` for detailed steps. The pattern is:

1. Create subgraph file in `backend/agent/workflows/subgraphs/`
2. Implement `summarize_node` that:
   - Fetches relevant context
   - Updates state with workflow context
   - Emits summary message
   - Clears `current_workflow` after completion
3. Register in `subgraphs/__init__.py` (intent detection)
4. Add to main graph in `graph.py`

**Note**: Guidance is handled in `chat_node` via system message, not in subgraphs.

## Benefits

1. **Scalability**: Easy to add new workflows without touching existing code
2. **Maintainability**: Each workflow is isolated and testable
3. **Consistency**: All workflows follow the same pattern
4. **Reusability**: Common logic in base class
5. **Flexibility**: Each workflow can customize steps as needed

