# Ecocash AI Relationship Manager – PRD

**Objective:** Deliver a conversational EcoCash relationship manager that combines chat and AG-UI widgets to handle wallet balances, transaction insights, and ticket workflows for retail customers within the mobile app.

**Technical Context:** CopilotKit web widget (AG-UI protocol) embedded in Ecocash mobile, backed by Agno AgentOS (v2.2.13) with MongoDB Atlas for sessions/memory, FastMCP v2 dummy wallet server (swappable for production MCP), and OpenAI GPT‑5 Mini streamed through AG-UI [[CopilotKit](https://www.copilotkit.ai)] [[AG-UI](https://docs.agno.com/agent-os/interfaces/ag-ui/introduction)].

**MVP Requirements:**

1. **Session Handling:** The mobile shell injects a signed JWT directly into the widget; the frontend forwards it to the backend (no server-side validation yet) and persists session metadata + history in MongoDB `ecocash-assistance-agent`.
2. **Structured Responses:** Agent responses must serialize AG-UI widgets (balance card, transaction table with CTA, ticket form, ticket status board, confirmation dialog) via the shared schema package so the frontend can render rich tiles alongside chat bubbles.
3. **FastMCP Integration:** Dummy FastMCP server exposes `eco_get_balances`, `eco_get_transactions`, `eco_create_ticket`, `eco_get_ticket_status`; Agno AgentOS consumes them through `MCPTools` (stdio) while passing along the mobile JWT for downstream authorization.
4. **Human-in-loop Controls:** Sensitive MCP mutations (ticket creation, account changes) require a confirmation widget summarizing the action; the agent must wait for the user’s postback before proceeding.
5. **Analytics & Observability:** Frontend emits widget view/action events; backend logs tool calls and errors with request IDs, enabling a future metrics pipeline (OpenTelemetry ready).
6. **Documentation & Test Harness:** README / architecture / milestones stay current, and the `mobile-wrapper.html` test harness simulates the native shell for end-to-end QA.

**Instructions for LLM:**

- Use only MCP data or stored memory; never synthesize transaction/balance details.
- Always send a conversational summary **and** an AG-UI widget when showing structured information. Transaction tables must include a `Get help` CTA that posts back `{ "type": "transaction_help", "transactionId": "<id>" }`.
- When a user taps “Get help” (or asks for help on a transaction), render a follow-up summary widget highlighting merchant, amount, time, and offer multiple reasons (Amount debited, Issue with offer, Refund issues, etc.).
- Request confirmation before executing `eco_create_ticket` or any irreversible action; summarize the action in the dialog.
- Prefer actionable suggestions (deeplinks, buttons) over free text where possible, mirroring ChatGPT-style quick actions.
- Log reasoning succinctly (“Eco Assist is preparing your card…”) but keep user-facing responses focused on outcomes.
