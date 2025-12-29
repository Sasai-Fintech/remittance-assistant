# Remittance AI Assistant

An AI-powered conversational assistant for international money transfers (remittances), built with CopilotKit, LangGraph, and Next.js. The assistant guides users through the complete remittance process - from checking exchange rates to completing secure payments - all through natural language interactions.

## ✨ Key Features

- 💱 **Real-time Exchange Rates**: Get live currency conversion rates for international transfers
- 🔒 **Rate Locking**: Lock favorable rates for your transactions  
- 📊 **Quote Generation**: Receive detailed remittance quotes with fees and recipient amounts
- 💳 **Multiple Payment Methods**: Choose from EFT, cash, or card payments
- 🔐 **Secure Payment Gateway**: Embedded payment processing with fallback support
- 🎯 **Conversational UX**: Complete the entire remittance flow through chat
- 📱 **Mobile Ready**: Flutter WebView integration for native mobile apps

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

3. **MCP Server Environment** (`mcp-remittance/.env`):
```bash
# Sasai Payment Gateway API
PAYMENT_GATEWAY_BASE_URL=https://sandbox.sasaipaymentgateway.com
PAYMENT_GATEWAY_USERNAME=your_username_here
PAYMENT_GATEWAY_PASSWORD=your_password_here
PAYMENT_GATEWAY_PIN=your_pin_here

# Optional: Logging
LOG_LEVEL=INFO
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
│   │   ├── chat.py        # Chat node with remittance workflow prompt
│   │   └── state.py       # Agent state definitions
│   └── pyproject.toml      # Poetry dependencies
├── mcp-remittance/         # Model Context Protocol server for remittance
│   ├── src/
│   │   ├── api/            # API client for payment gateway
│   │   │   └── client.py  # HTTP client for Sasai Payment Gateway
│   │   └── remittance/     # MCP tool implementations
│   │       ├── countries.py    # Exchange rates & MCP tool registration
│   │       ├── rates.py        # Rate locking functionality
│   │       ├── quotes.py       # Quote generation
│   │       ├── payments.py     # Payment options retrieval
│   │       └── transactions.py # Transaction execution
│   └── pyproject.toml      # FastMCP dependencies
├── frontend/               # Next.js frontend
│   ├── app/                # Next.js app directory
│   │   ├── page.tsx       # Main chat interface
│   │   └── api/            # API routes
│   │       └── copilotkit/ # CopilotKit runtime endpoint
│   ├── components/         # React components
│   │   ├── widgets/        # AG-UI widget components
│   │   │   ├── ExchangeRateCard.tsx
│   │   │   ├── RateLockConfirmation.tsx
│   │   │   ├── QuoteDetailsCard.tsx
│   │   │   ├── PaymentOptionsCard.tsx
│   │   │   ├── PaymentGatewayWidget.tsx  # Embedded payment with fallback
│   │   │   └── TransactionReceipt.tsx
│   │   ├── RemittanceWidgets.tsx  # Widget registry
│   │   └── ui/             # Radix UI primitives
│   └── lib/                # Utilities and types
├── packages/
│   └── schemas/            # Shared TypeScript schemas
├── docs/                   # Project documentation
│   ├── prd.md             # Product Requirements Document
│   ├── architecture.md    # Architecture overview
│   ├── REMITTANCE_USER_JOURNEY.md  # Complete user flow
│   ├── FLOW_3_QUOTE_GENERATION_COMPLETE.md  # Quote flow details
│   ├── FLOW_4_TRANSACTION_COMPLETE.md       # Transaction flow
│   ├── PAYMENT_METHOD_SELECTION_FLOW.md     # Payment selection
│   ├── PATCH_TRANSACTION_SIMPLIFICATION.md  # API payload docs
│   ├── EMBEDDED_PAYMENT_GATEWAY.md          # Widget documentation
│   ├── PAYMENT_GATEWAY_IFRAME_FALLBACK.md   # Fallback behavior
│   └── ...                # Additional guides
└── start.sh               # Convenience startup script
```

## 🎯 Features

### Complete Remittance Flow

The assistant guides users through a 4-step remittance process:

#### **Step 1: Exchange Rate Inquiry**
- Get real-time exchange rates between currencies
- View conversion rates and compare options
- Ask: "What's the exchange rate from ZAR to USD?"

#### **Step 2: Rate Locking**
- Lock favorable exchange rates for your transaction
- Receive a calculation ID for the locked rate
- Valid for a specific time period
- Ask: "Lock the rate for sending R1000 to USD"

#### **Step 3: Quote Generation**
- Generate detailed remittance quote
- View breakdown: sending amount, fees, recipient amount
- Includes beneficiary details and payout method
- Receive transaction ID for payment
- Ask: "Create a quote for John Doe via EcoCash"

#### **Step 4: Payment & Execution**

**Step 4a - Payment Method Selection**
- View available payment options (EFT, Cash, Card)
- See provider details and instructions
- Interactive payment selection widget
- Ask: "Show me payment options"

**Step 4b - Transaction Execution**
- Execute transaction with selected payment method
- Receive secure payment gateway URL
- Complete payment in embedded iframe or new window
- Get transaction confirmation

### Payment Gateway Widget

The assistant includes an intelligent payment gateway widget that:

✅ **Attempts embedded iframe first** for seamless in-chat payment  
✅ **Auto-detects iframe blocking** (X-Frame-Options/CSP)  
✅ **Shows beautiful fallback UI** with prominent "Open Payment Gateway" button  
✅ **Displays transaction summary** (ID, recipient, amounts)  
✅ **Full-screen mode** for better viewing experience  
✅ **Security badges** and SSL indicators  
✅ **Dark mode support** matching chat theme

**Fallback Behavior**: When payment gateways block iframe embedding (common security practice), the widget automatically displays a professional call-to-action to open the payment page in a new secure window.

### Additional Capabilities

1. **Balance Checking**: Query wallet balances through natural language
2. **Transaction History**: View recent transactions with structured data
3. **Transaction Help**: Context-aware transaction assistance with automatic detail fetching
4. **Support Tickets**: Create support tickets with human-in-the-loop confirmation
5. **Mobile Integration**: Flutter WebView integration with JWT authentication and context passing
6. **Conversational Interface**: Natural language interactions powered by Azure OpenAI GPT-4o-mini

### Agent Tools

The backend agent exposes the following MCP tools:

#### Remittance Flow Tools
- `get_exchange_rates(from_currency, to_currency, country_code)`: Get real-time exchange rates
- `lock_exchange_rate(from_currency, to_currency, amount, country_code)`: Lock rate and get calculation ID
- `generate_remittance_quote(calculation_id, beneficiary_details)`: Generate detailed quote with transaction ID
- `get_payment_options(service_type)`: Fetch available payment methods (EFT, cash, card)
- `execute_remittance_transaction(transaction_id, payment_method_code)`: Execute payment and get gateway URL

#### Legacy Tools
- `get_balance(user_id: str)`: Retrieve wallet balance
- `list_transactions(user_id: str, limit: int)`: List recent transactions
- `get_transaction_details(user_id: str, transaction_id: str)`: Get detailed transaction information
- `create_ticket(user_id: str, subject: str, body: str)`: Create a support ticket

### Widget Components

The frontend includes interactive widget components using CopilotKit generative UI:

#### Remittance Widgets
- `ExchangeRateCard`: Displays live exchange rates with currency flags and conversion details
- `RateLockConfirmation`: Shows locked rate with expiry time and calculation ID
- `QuoteDetailsCard`: Comprehensive quote breakdown with fees and recipient amounts
- `PaymentOptionsCard`: Interactive payment method selector with provider details
- `PaymentGatewayWidget`: Embedded payment gateway with iframe fallback
- `TransactionReceipt`: Final confirmation with transaction details

#### Legacy Widgets
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

### MCP Server Development

```bash
cd mcp-remittance
poetry install
poetry run mcp dev src/remittance/countries.py
```

The MCP server provides remittance tools via FastMCP. Tools are registered in:
- `countries.py` - Exchange rates and tool registration
- `rates.py` - Rate locking
- `quotes.py` - Quote generation  
- `payments.py` - Payment options
- `transactions.py` - Transaction execution

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

The frontend uses CopilotKit for the chat interface. The main chat component is in `frontend/app/page.tsx`.

#### Widget Development

Widgets are registered in `frontend/components/RemittanceWidgets.tsx` using CopilotKit's `useCopilotAction`:

```tsx
useCopilotAction({
  name: "tool_name",
  description: "Tool description",
  parameters: [/* ... */],
  handler: async (args) => {
    // Handle the action
    return result;
  },
  render: ({ result }) => {
    // Render the widget
    return <YourWidget {...result} />;
  }
});
```

#### Payment Gateway Widget

The `PaymentGatewayWidget` component (`frontend/components/widgets/PaymentGatewayWidget.tsx`) handles:

1. **Embedded Iframe**: Attempts to load payment gateway in iframe
2. **Auto-detection**: Detects if iframe is blocked (3s timeout + error handler)
3. **Fallback UI**: Shows prominent button when iframe fails
4. **Full-screen Mode**: Toggle for better viewing
5. **Security**: Sandbox attributes and SSL indicators

**Key Props:**
- `transactionUrl` - Payment gateway URL (required)
- `transactionId` - Transaction identifier (required)
- `recipientName`, `sendingAmount`, `recipientAmount` - Display info (optional)

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
- [Technical Decisions](./docs/decisions.md) - Architecture and design decisions

### Remittance Flow Documentation
- [Remittance User Journey](./REMITTANCE_USER_JOURNEY.md) - Complete 4-step flow overview
- [Flow 3: Quote Generation](./FLOW_3_QUOTE_GENERATION_COMPLETE.md) - Quote creation details
- [Flow 4: Transaction Execution](./FLOW_4_TRANSACTION_COMPLETE.md) - Payment execution
- [Payment Method Selection](./PAYMENT_METHOD_SELECTION_FLOW.md) - Payment options flow
- [PATCH Transaction Simplification](./PATCH_TRANSACTION_SIMPLIFICATION.md) - API payload structure
- [Embedded Payment Gateway](./EMBEDDED_PAYMENT_GATEWAY.md) - Widget implementation
- [Payment Gateway Iframe Fallback](./PAYMENT_GATEWAY_IFRAME_FALLBACK.md) - Fallback behavior

### Setup & Development Guides
- [Quick Start Guide](./docs/quick-start-local.md) - Local development setup
- [Docker Setup](./docs/docker-setup.md) - Containerized deployment
- [Local PostgreSQL Setup](./docs/local-postgres-setup.md) - Database setup
- [Quick Start Guide](./QUICK_START_GUIDE.md) - Getting started with remittance flows

### Integration Guides
- [Flutter Mobile Integration](./docs/mobile-integration.md) - WebView integration for mobile apps
- [Azure Deployment](./docs/azure-deploy.md) - Cloud deployment guide
- [MCP Server Setup](./docs/mcp-server-setup.md) - Model Context Protocol configuration

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

### Testing the Remittance Flow

Try these example conversations:

**Exchange Rates:**
```
"What's the exchange rate from South African Rand to US Dollars?"
"Show me ZAR to USD conversion rates"
```

**Lock Rate & Create Quote:**
```
"Lock the rate for sending R1000 to USD"
"Create a quote to send money to John Doe via EcoCash"
```

**Payment & Execution:**
```
"Show me payment options"
"I want to pay with EFT"
"Execute the transaction with card payment"
```

### Payment Gateway Testing

The payment gateway widget has two behaviors:

1. **Embedded Mode**: If the payment gateway allows iframe embedding, you'll see the payment page directly in the chat
2. **Fallback Mode**: If blocked (X-Frame-Options/CSP), you'll see a prominent "Open Payment Gateway" button

Test both scenarios by checking different payment gateway configurations.

### MCP Server Integration

The remittance flows use FastMCP (Model Context Protocol) to connect to the Sasai Payment Gateway API:

- **Endpoint**: `sandbox.sasaipaymentgateway.com`
- **Authentication**: Bearer token from wallet credentials
- **Tools**: Registered via FastMCP decorators in `/mcp-remittance/src/remittance/`

In production, ensure:
- Valid API credentials in environment variables
- Network access to payment gateway
- Proper SSL certificate validation
- Rate limiting and retry logic

## 🔐 Security Notes

- ⚠️ Environment variables should never be committed to version control
- 🔑 Azure OpenAI API keys must be kept secure
- 🔐 Payment gateway credentials stored in MCP server environment
- 👤 JWT validation should be implemented for production use
- 🚦 Rate limiting should be added for API endpoints
- ✅ All sensitive operations require human-in-the-loop confirmation
- 🛡️ Payment gateway widget uses secure iframe sandbox attributes
- 🔒 Fallback to new tab maintains security when iframe is blocked
- 📜 X-Frame-Options and CSP headers respected for payment security

## 🚧 Roadmap

### Completed Features ✅
- ✅ Complete 4-step remittance flow (rates → lock → quote → payment)
- ✅ Real-time exchange rate integration
- ✅ Rate locking with calculation IDs
- ✅ Quote generation with beneficiary details
- ✅ Payment method selection (EFT/Cash/Card)
- ✅ Transaction execution with PATCH API
- ✅ Embedded payment gateway widget
- ✅ Iframe fallback for blocked payment gateways
- ✅ Interactive CopilotKit generative UI widgets
- ✅ MCP (Model Context Protocol) integration
- ✅ Azure OpenAI GPT-4o-mini integration

### In Progress 🚧
- 🚧 Payment confirmation webhook handling
- 🚧 Transaction status polling
- 🚧 Error recovery flows
- 🚧 Multi-language support (English/Shona)

### Planned Features ⏳
- ⏳ Transaction history for remittances
- ⏳ Beneficiary management (save recipients)
- ⏳ Recurring remittance scheduling
- ⏳ Push notifications for transaction updates
- ⏳ Enhanced mobile app integration
- ⏳ Compliance & KYC workflows
- ⏳ Analytics dashboard

See [milestones.md](./docs/milestones.md) for detailed implementation roadmap.

## � Common Issues & Solutions

### Payment Gateway Iframe Blocked

**Issue**: `stag20-za.securemit.com refused to connect` error in iframe

**Cause**: Payment gateway blocks iframe embedding using X-Frame-Options or Content-Security-Policy headers (common security practice)

**Solution**: ✅ Already handled! The widget automatically:
1. Detects iframe blocking (3-second timeout + error handler)
2. Shows fallback UI with prominent "Open Payment Gateway" button
3. Opens payment page in new secure window
4. Maintains transaction context and security

See [PAYMENT_GATEWAY_IFRAME_FALLBACK.md](./PAYMENT_GATEWAY_IFRAME_FALLBACK.md) for details.

### MCP Server Connection Failed

**Issue**: Backend cannot connect to MCP server

**Solutions**:
- Verify MCP server is running: `cd mcp-remittance && poetry run mcp dev`
- Check environment variables for API credentials
- Ensure network access to `sandbox.sasaipaymentgateway.com`
- Verify authentication token is valid

### Widget Not Rendering

**Issue**: Widget components not displaying in chat

**Solutions**:
- Check widget is registered in `RemittanceWidgets.tsx`
- Verify tool name matches between backend and frontend
- Check browser console for React errors
- Ensure result object has required fields for widget props

### Exchange Rate API Timeout

**Issue**: Exchange rate queries timeout or fail

**Solutions**:
- Verify API endpoint accessibility
- Check rate limiting on payment gateway
- Implement retry logic with exponential backoff
- Cache exchange rates for brief periods

## �📝 License

[Add your license here]

## 🤝 Contributing

[Add contributing guidelines here]

