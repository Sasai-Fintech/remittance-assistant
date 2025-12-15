# Testing Checklist

This checklist ensures the EcoCash Assistant works correctly after code changes.

## Pre-Deployment Checks

### Backend Health

- [ ] Backend starts without errors: `cd backend && poetry run uvicorn app.main:app --reload`
- [ ] Graph compiles successfully: `poetry run python -c "from agent.graph import build_graph; build_graph()"`
- [ ] `/api/copilotkit/info` endpoint returns 200 (not 500)
  ```bash
  curl http://localhost:8000/api/copilotkit/info
  ```
- [ ] No import errors in backend logs (especially `CompiledGraph` import issues)

### Frontend Health

- [ ] Frontend starts without errors: `cd frontend && npm run dev`
- [ ] No console errors in browser DevTools
- [ ] CopilotKit connects to backend (check Network tab for `/api/copilotkit` requests)

### Subgraph Tests

- [ ] Run subgraph test suite: `poetry run python backend/test_subgraphs.py`
- [ ] All subgraphs compile and execute without errors
- [ ] State management works (context fields set, `current_workflow` cleared)

## Functional Testing

### Basic Chat

- [ ] User can send messages
- [ ] AI responds appropriately
- [ ] Suggestions appear below chat input
- [ ] Suggestions are context-aware (not redundant)

### Balance Check

- [ ] User asks: "Check my balance"
- [ ] Balance card widget appears
- [ ] Balance amount is displayed correctly

### Transaction History

- [ ] User asks: "Show my transactions" or "View transactions"
- [ ] Transaction grid appears (horizontally scrollable)
- [ ] Each transaction card shows: merchant, date, amount
- [ ] Support CTA button is visible on each card

### Transaction Help Workflow

- [ ] User clicks "Help" on a transaction card
- [ ] Message is sent: "I need help with my transaction to [merchant]..."
- [ ] Transaction is immediately summarized with UTR
- [ ] AI asks: "Tell us what's wrong"
- [ ] Suggestions show common transaction issues:
  - "Receiver has not received the payment"
  - "Amount debited twice"
  - "Transaction failed"
  - "Need refund"
  - "Wrong amount charged"
  - "Offer not applied"
- [ ] User selects an issue (e.g., "Receiver has not received")
- [ ] AI provides guidance with UTR and steps
- [ ] Suggestions update to: "Okay", "Contacted merchant, issue not resolved", "Issue resolved"

### Ticket Creation

- [ ] User explicitly requests ticket or says issue not resolved
- [ ] Ticket confirmation dialog appears
- [ ] Dialog shows:
  - Subject (extracted from conversation, not blank)
  - Body (detailed description, not blank)
  - Confirm button
  - Cancel button
- [ ] User clicks "Confirm"
- [ ] Ticket is created (no repeated confirmation)
- [ ] Success message shows ticket ID prominently
- [ ] Suggestions update to: "Check my balance", "View transactions", "Ask another question"
- [ ] Suggestions do NOT show "Confirm submission" after ticket is created

### Other Workflows

- [ ] Refund workflow: User says "I need a refund" → Subgraph summarizes → Chat continues
- [ ] Loan enquiry: User says "loan" → Subgraph summarizes → Chat continues
- [ ] Card issue: User says "card" → Subgraph summarizes → Chat continues
- [ ] General enquiry: User says "help" → Subgraph summarizes → Chat continues

### State Lifecycle

- [ ] After subgraph completes, new intents can be detected
- [ ] `current_workflow` is cleared after subgraph completion
- [ ] Workflow context persists for `chat_node` to use

## Edge Cases

### Error Handling

- [ ] Backend tool failures don't crash the app
- [ ] Error messages are user-friendly
- [ ] Logs show error details for debugging

### Multiple Workflows

- [ ] User can switch between workflows in same session
- [ ] State doesn't leak between workflows
- [ ] Each workflow maintains its own context

### Network Issues

- [ ] Frontend handles backend disconnection gracefully
- [ ] Messages queue properly when backend is down
- [ ] Reconnection works automatically

## Performance

- [ ] Suggestions load within 2 seconds
- [ ] Widgets render within 1 second after tool call
- [ ] Chat responses are responsive (< 5 seconds for simple queries)
- [ ] No memory leaks during extended use

## Browser Compatibility

- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

## Logging

- [ ] Backend logs show intent detection
- [ ] Backend logs show subgraph entry/exit
- [ ] Backend logs show tool invocations
- [ ] Error logs include stack traces
- [ ] Debug logs are available for troubleshooting

## Documentation

- [ ] `LANGGRAPH_SUBGRAPH_GUIDE.md` is up to date
- [ ] `ADDING_NEW_WORKFLOW.md` reflects current implementation
- [ ] `SCALING_ARCHITECTURE.md` matches directory structure
- [ ] Code comments explain complex logic

## Quick Smoke Test

Run this minimal test after any backend changes:

```bash
# 1. Check backend health
curl http://localhost:8000/api/copilotkit/info

# 2. Check graph compiles
cd backend && poetry run python -c "from agent.graph import build_graph; build_graph()"

# 3. Check subgraphs
poetry run python backend/test_subgraphs.py
```

If all three pass, the backend is healthy.

## After Code Changes

Always test:
1. `/api/copilotkit/info` endpoint (critical for suggestions)
2. Graph compilation (catches import errors)
3. At least one end-to-end workflow (transaction help + ticket creation)
4. Suggestions appear and are context-aware

