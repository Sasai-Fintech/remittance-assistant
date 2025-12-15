# Balance Check Journey

**Objective:** Give retail users immediate clarity on wallet balances as soon as Eco Assist opens.
**Technical Context:** CopilotKit widget auto-loads after session bootstrap; Agno AgentOS fetches balance data via FastMCP `get_balances`.
**Requirements:**

1. Widget renders multi-account balance card with available funds, limits, and deeplink buttons (`ecocash://wallet/...`).
2. Agent references last widget state when user follows up (“show USD limits”).
3. Analytics records widget impressions and deeplink clicks for product insights.
   **Instructions for LLM:**

- Trigger `get_balances` tool when balance info is missing or stale.
- Prefer AG-UI cards; respond with text only for explanatory context.
- Offer quick actions (“View transactions”, “Set alert”) tied to postback payloads.

# Transaction History Journey

**Objective:** Let users browse, filter, and dispute recent transactions without leaving chat.
**Technical Context:** AG-UI transaction table widget fed by FastMCP `get_transactions`; filters handled client-side (chips) but payload stored in memory.
**Requirements:**

1. Support pagination cursor metadata from MCP response (even if mocked for now).
2. Provide deeplinks per transaction to open native details screen.
3. Include “Report issue” button to branch into ticket flow with selected transaction context.
   **Instructions for LLM:**

- Always pass user_id + limit when calling `get_transactions`.
- Annotate widget actions with postback payload referencing transaction ID.
- Cache last result in session memory for follow-up clarification (“What was txn-002 status?”).

# Ticket Creation Journey

**Objective:** Convert complaints into structured tickets with minimum typing.
**Technical Context:** Multi-step ticket form widget (category select, description textarea) and confirmation dialog; backend uses FastMCP `create_ticket`.
**Requirements:**

1. Collect transaction reference automatically if triggered from transaction widget.
2. Summarize captured info before confirmation; log user approval outcome.
3. Persist ticket metadata (ID, summary, status) in MongoDB for quick retrieval.
   **Instructions for LLM:**

- Request confirmation widget prior to calling `create_ticket`.
- On rejection, provide alternative help suggestions and keep audit log.
- After success, emit ticket card plus deeplink to native support hub.

# Ticket Status Journey

**Objective:** Show open tickets, latest updates, and escalation options.
**Technical Context:** FastMCP `get_ticket_status` feeds AG-UI ticket board; backend caches results for push updates via websocket (future).
**Requirements:**

1. Display status chips (new, in_progress, pending_customer, resolved, closed) with consistent colors.
2. Offer “Escalate” or “Add info” buttons (postbacks) for future enhancements.
3. Sync board state whenever MCP returns changes (polling interval configurable).
   **Instructions for LLM:**

- Refresh status if cached data older than configurable SLA (e.g., 2 minutes).
- Reference ticket ID when clarifying follow-up messages.
- Provide empathetic, action-oriented tone for pending/resolved states.

# Human-in-Loop Confirmation Journey

**Objective:** Ensure sensitive actions (ticket creation, statement sharing) require explicit consent.
**Technical Context:** AG-UI confirmation dialog widget; backend enforces gating before MCP mutation tools run.
**Requirements:**

1. Dialog displays summary, risk level, and buttons (“Confirm”, “Cancel”).
2. Agent logs decision + rationale to MongoDB audit collection.
3. Decline path offers safe alternatives (e.g., “Chat with agent later”).
   **Instructions for LLM:**

- Block tool execution until confirmation result captured.
- Escalate to human support if user repeatedly declines but issue remains unresolved.
- Include reminder about data privacy when sharing statements or PII.
