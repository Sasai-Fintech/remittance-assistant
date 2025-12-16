# Remittance AI Assistant

An AI-powered conversational assistant for Remittance fintech services, built with CopilotKit, LangGraph, and Next.js. The assistant helps users manage their wallet balances, view transactions, and create support tickets through natural language interactions.

## 🏗️ Architecture

This is a monorepo containing:

- **Backend** (`/backend`): FastAPI server with LangGraph agent powered by OpenAI
- **Frontend** (`/frontend`): Next.js application with CopilotKit React components
- **Schemas** (`/packages/schemas`): Shared TypeScript/Zod schemas for type-safe widget communication

### Technology Stack

**Backend:**
- Python 3.12
- FastAPI
- LangGraph (agent orchestration)
- CopilotKit (AG-UI protocol)
- Azure OpenAI GPT-4o-mini (cost-effective LLM)
- Poetry (dependency management)

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- CopilotKit React
- Tailwind CSS
- Radix UI components

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- Poetry (for Python dependency management)
- npm or pnpm

### Environment Setup

1. **Backend Environment** (`backend/.env`):
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://azureopenai-uswest-sandbox.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

2. **Frontend Environment** (`frontend/.env.local`):
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://azureopenai-uswest-sandbox.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Backend API URL
REMOTE_ACTION_URL=http://localhost:8000/api/copilotkit
```

### Installation & Running

#### Option 1: Using the Start Script (Recommended)

```bash
chmod +x start.sh
./start.sh
```

This will start both backend and frontend services automatically.

#### Option 2: Manual Setup

**Backend:**
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Backend Health Check**: http://localhost:8000/

## 📁 Project Structure

```
remittance-assistant/
├── backend/                 # Python FastAPI backend
│   ├── agent/              # LangGraph agent definition
│   │   ├── graph.py       # Agent workflow graph
│   │   └── tools.py       # Agent tools (placeholder implementations)
│   ├── app/                # FastAPI application
│   │   └── main.py        # FastAPI entry point
│   ├── engine/             # Agent engine components
│   │   ├── chat.py        # Chat node implementation
│   │   └── state.py       # Agent state definitions
│   ├── mcp/                # MCP tools (future integration)
│   └── pyproject.toml      # Poetry dependencies
├── frontend/               # Next.js frontend
│   ├── app/                # Next.js app directory
│   │   ├── page.tsx       # Main chat interface
│   │   └── api/            # API routes
│   │       └── copilotkit/ # CopilotKit runtime endpoint
│   ├── components/         # React components
│   │   ├── widgets/        # AG-UI widget components
│   │   └── ui/             # Radix UI primitives
│   └── lib/                # Utilities and types
├── packages/
│   └── schemas/            # Shared TypeScript schemas
├── docs/                   # Project documentation
│   ├── prd.md             # Product Requirements Document
│   ├── architecture.md    # Architecture overview
│   ├── milestones.md      # Implementation milestones
│   ├── user-journeys.md   # User journey definitions
│   ├── decisions.md       # Technical decisions log
│   ├── mobile-integration.md  # Flutter mobile integration guide
│   ├── quick-start-local.md   # Local development setup
│   └── ...                # Additional guides (see Documentation section)
└── start.sh               # Convenience startup script
```

## 🎯 Features

### Current Capabilities

1. **Balance Checking**: Query wallet balances through natural language
2. **Transaction History**: View recent transactions with structured data
3. **Transaction Help**: Context-aware transaction assistance with automatic detail fetching
4. **Support Tickets**: Create support tickets with human-in-the-loop confirmation
5. **Mobile Integration**: Flutter WebView integration with JWT authentication and context passing
6. **Conversational Interface**: Natural language interactions powered by GPT-4o-mini

### Agent Tools

The backend agent exposes the following tools:

- `get_balance(user_id: str)`: Retrieve wallet balance
- `list_transactions(user_id: str, limit: int)`: List recent transactions
- `get_transaction_details(user_id: str, transaction_id: str)`: Get detailed transaction information
- `create_ticket(user_id: str, subject: str, body: str)`: Create a support ticket

### Widget Components

The frontend includes reusable widget components:

- `BalanceCard`: Displays wallet balance with currency formatting
- `TransactionTable`: Shows transaction history in a table format
- `TicketConfirmation`: Human-in-the-loop confirmation dialog

## 🔧 Development

### Backend Development

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload --port 8000
```

The backend uses LangGraph for agent orchestration. The agent graph is defined in `backend/agent/graph.py` and uses nodes from `backend/engine/chat.py`.

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

The frontend uses CopilotKit for the chat interface. The main chat component is in `frontend/app/page.tsx`.

### Schema Package

The shared schemas package provides type-safe communication between frontend and backend:

```bash
cd packages/schemas
npm install
npm run build
```

## 📚 Documentation

### Core Documentation
- [Product Requirements Document](./docs/prd.md) - Product specs and requirements
- [Architecture Overview](./docs/architecture.md) - System architecture and design
- [Implementation Milestones](./docs/milestones.md) - Development roadmap
- [User Journeys](./docs/user-journeys.md) - User experience flows
- [Technical Decisions](./docs/decisions.md) - Architecture and design decisions

### Setup & Development Guides
- [Quick Start Guide](./docs/quick-start-local.md) - Local development setup
- [Docker Setup](./docs/docker-setup.md) - Containerized deployment
- [Local PostgreSQL Setup](./docs/local-postgres-setup.md) - Database setup

### Integration Guides
- [Flutter Mobile Integration](./docs/mobile-integration.md) - WebView integration for mobile apps
- [Azure Deployment](./docs/azure-deploy.md) - Cloud deployment guide

### Development Guides
- [Adding New Workflow](./docs/adding-new-workflow.md) - Creating new agent workflows
- [LangGraph Subgraph Guide](./docs/langgraph-subgraph-guide.md) - Subgraph development
- [Testing Checklist](./docs/testing-checklist.md) - Testing procedures

### Scaling & Performance
- [Scaling Architecture](./docs/scaling-architecture.md) - Scalability patterns
- [Scaling Implementation](./docs/scaling-implementation.md) - Implementation details
- [Scaling Quick Start](./docs/scaling-quick-start.md) - Quick scaling guide

### Component Documentation
- [Backend README](./backend/README.md) - Backend-specific documentation
- [Frontend README](./frontend/README.md) - Frontend-specific documentation

## 🧪 Testing

Currently, the project uses placeholder implementations for tools. In production, these would connect to:

- Real wallet/balance APIs
- Transaction databases
- Ticket management systems
- MCP (Model Context Protocol) servers

## 🔐 Security Notes

- Environment variables should never be committed to version control
- JWT validation should be implemented for production use
- Rate limiting should be added for API endpoints
- All sensitive operations require human-in-the-loop confirmation

## 🚧 Roadmap

See [milestones.md](./docs/milestones.md) for detailed implementation roadmap:

- ✅ Milestone 1: Foundations & Architecture
- 🚧 Milestone 2: CopilotKit Widget & UX
- 🚧 Milestone 3: Agno AgentOS Backend
- ⏳ Milestone 4: Ticket Workflow & Human-in-loop
- ⏳ Milestone 5: Quality, Compliance & Launch

## 📝 License

[Add your license here]

## 🤝 Contributing

[Add contributing guidelines here]

