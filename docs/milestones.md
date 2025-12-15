# Implementation Milestones

## Milestone 1 – Foundations & Architecture ✅ (complete)

**Objective:** Mono-repo scaffolding, env management, shared schema package, architecture docs.
**Deliverables:**

1. PNPM/Turbo workspace + linting/formatting + Husky hooks.
2. Backend/Frontend config loaders, consolidated envs under `configs/.env`.
3. `@ecocash/schemas` workspace published + consumed via TS path alias.
4. Architecture + PRD + user journey docs committed; mobile wrapper for testing.

## Milestone 2 – CopilotKit Widget & UX 🚧 (MVP working, polishing ongoing)

**Objective:** Ship embedded CopilotKit experience with AG-UI renderer, deeplinks, analytics, Storybook.
**Status Highlights:**

1. Custom chat layout, session history, and quick actions are live.
2. AG-UI renderer supports all MVP widgets; widget payloads validated via shared schemas.
3. Deeplink bridge + analytics hook implemented (pending analytics backend wiring).
4. Storybook stubs exist; need to finish component stories + visual tests.

## Milestone 3 – Agno AgentOS Backend 🚧 (core functionality complete)

**Objective:** Production-ready AgentOS runtime with MCP tools, memory, observability.
**Status Highlights:**

1. Agno AgentOS v2.2.13 integrated with FastAPI + JWT passthrough middleware.
2. FastMCP dummy server auto-launched; agent instructions enforce widget usage + confirmations.
3. MongoDB persistence wired through AgentOS; in-memory option for tests.
4. Need to add metrics exporters & production MCP endpoints.

## Milestone 4 – Ticket Workflow & Human-in-loop ⏳ (not started)

**Objective:** Ticket creation/status flows with confirmation gating and notification plumbing.
**Requirements:**

1. Multi-step ticket forms with transaction context.
2. Confirmation dialogs enforced before `create_ticket`.
3. Ticket status board + optional push updates for state changes.
4. Documented human-in-loop/fallback policies.

## Milestone 5 – Quality, Compliance & Launch ⏳ (not started)

**Objective:** Harden stack, add automated tests, monitoring, and rollout playbooks.
**Requirements:**

1. Regression + integration tests (backend MCP tools, frontend flows).
2. Security review: token validation, rate limiting, secret handling.
3. Monitoring dashboards (latency, tool errors, widget usage) + runbooks.
4. Staging/UAT sign-off, release notes for mobile integration.
