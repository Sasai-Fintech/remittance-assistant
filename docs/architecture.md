# Ecocash AI Relationship Manager – Architecture Overview

## Components

1. **Mobile Shell** – Native Ecocash app hosting the CopilotKit widget inside a secure web view. Supplies an ephemeral JWT + metadata (channel, device info) via query params / JS bridge.
2. **Frontend Widget (`/frontend`)** – Next.js/CopilotKit app with custom chat UI, AG-UI renderer, session history, analytics hooks, and deeplink bridge to native routes. It parses the JWT client-side and forwards it to all CopilotKit requests.
3. **Backend AgentOS (`/backend`)** – FastAPI base + Agno AgentOS runtime. Exposes `/agui` for CopilotKit, handles MongoDB persistence, launches the FastMCP dummy wallet/ticket server, and injects the mobile JWT into MCP tool contexts.
4. **Schema Package (`/packages/schemas`)** – Shared Zod (frontend) + mirrored Pydantic (backend) models for AG-UI widgets, ensuring strict validation.
5. **External Services** – MongoDB Atlas (sessions, memory), OpenAI GPT‑5 Mini, FastMCP wallet/ticket APIs (dummy now, replaceable with production endpoints), analytics pipeline (future).

## Request Flow

1. Mobile loads widget, injects JWT + metadata through query params/JS bridge.
2. Frontend parses token (no backend validation for MVP), stores session metadata locally, and starts CopilotKit with headers `{ Authorization: Bearer <JWT> }`.
3. CopilotKit runtime (`/api/copilotkit`) proxies requests to the backend AG-UI endpoint (`/agui`) while preserving headers.
4. Agno Agent processes the prompt, logs reasoning, invokes FastMCP tools (wallet/ticket) with the JWT, and writes session/memory to MongoDB.
5. When the agent emits `render_widget` / `request_confirmation`, the frontend validates payloads via `@ecocash/schemas` and renders AG-UI cards inline; user taps post back structured payloads which re-enter the conversation loop.
6. Analytics + deeplink interactions are captured on the frontend; backend logs tool usage for future telemetry.

## Data Stores

- `sessions` collection – session metadata, mobile token hash, expiry.
- `agent_events` (via AgentOS Mongo) – transcripts, widget references, tool logs.
- `memory` collections – short/long term memories (AgentOS default tables).
- Future: `vector_memory` for embeddings, `tickets` cache for quick status lookup.

## Security

- JWT is trusted from the mobile shell for MVP and simply forwarded to backend + MCP; full verification / JWKS lookup is planned for production.
- Sensitive tool calls require confirmation captured in audit logs.
- All secrets loaded via typed config loader; `.env` files never committed (see `configs/sample.env`).

## Observability

- Structured logs (JSON) with request IDs (FastAPI + AgentOS).
- Metrics for MCP tool latency/success (to be published via OTLP).
- Frontend analytics hook (`trackEvent`) for widget views/actions; events can be forwarded to Segment/Firebase later.
- Mobile wrapper (`frontend/public/mobile-wrapper.html`) reproduces the native embedding scenario for manual and automated QA.
