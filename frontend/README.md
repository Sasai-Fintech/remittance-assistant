# EcoCash Assistant Frontend

Next.js frontend application for the EcoCash AI Assistant. Built with CopilotKit React components, providing a conversational interface with rich widget support for wallet management, transactions, and support tickets.

## 🏗️ Architecture

The frontend is built with:

- **Next.js 14**: React framework with App Router
- **CopilotKit React**: Chat interface and AG-UI widget rendering
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Radix UI**: Accessible component primitives
- **React 18**: Modern React features

## 📋 Prerequisites

- Node.js 18+ 
- npm, pnpm, or yarn

## 🚀 Setup

### 1. Install Dependencies

```bash
npm install
# or
pnpm install
# or
yarn install
```

### 2. Environment Configuration

Create a `.env.local` file in the `frontend/` directory:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://azureopenai-uswest-sandbox.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Backend API URL
REMOTE_ACTION_URL=http://localhost:8000/api/copilotkit
```

**Note**: The `.env.local` file is gitignored and should never be committed.

### 3. Run the Development Server

```bash
npm run dev
# or
pnpm dev
# or
yarn dev
```

The application will be available at `http://localhost:3000`.

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Main chat interface page
│   ├── layout.tsx         # Root layout with global styles
│   ├── globals.css        # Global CSS styles
│   └── api/               # API routes
│       └── copilotkit/    # CopilotKit runtime endpoint
│           └── route.ts   # Next.js API route handler
├── components/            # React components
│   ├── widgets/          # AG-UI widget components
│   │   ├── BalanceCard.tsx
│   │   ├── TransactionTable.tsx
│   │   └── TicketConfirmation.tsx
│   ├── ui/               # Radix UI primitives
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── ... (other UI components)
│   └── ... (other components)
├── lib/                  # Utilities and types
│   ├── types.ts          # TypeScript type definitions
│   ├── utils.ts          # Utility functions
│   └── hooks/            # Custom React hooks
├── public/               # Static assets
└── package.json         # Dependencies and scripts
```

## 🎨 Components

### Main Components

#### `app/page.tsx`
The main chat interface page that:
- Sets up CopilotKit provider
- Renders the chat UI
- Displays the balance card widget
- Handles agent communication

#### `app/api/copilotkit/route.ts`
Next.js API route that:
- Configures CopilotKit runtime
- Connects to backend agent
- Handles streaming responses
- Supports LangGraph Cloud deployments

### Widget Components

#### `BalanceCard`
Displays wallet balance with:
- Currency formatting
- Loading states
- Gradient styling
- Real-time updates from agent

#### `TransactionTable`
Shows transaction history with:
- Table layout
- Date, merchant, amount columns
- Currency formatting
- Card container

#### `TicketConfirmation`
Human-in-the-loop confirmation dialog with:
- Issue and description display
- Confirm/Cancel actions
- Integration with CopilotKit chat

### UI Components

The `components/ui/` directory contains Radix UI-based components:
- `button`: Button component with variants
- `card`: Card container component
- `dialog`: Modal dialog component
- `table`: Table components
- And more...

## 🔧 Development

### Adding New Widgets

1. Create widget component in `components/widgets/`:
```typescript
"use client";

import { Card } from "@/components/ui/card";

export function MyWidget({ data }: { data: MyDataType }) {
  return (
    <Card>
      {/* Widget content */}
    </Card>
  );
}
```

2. Register with CopilotKit using `useCopilotAction` or `useCopilotReadable`:
```typescript
useCopilotAction({
  name: "my_widget",
  description: "Display my widget",
  handler: async () => {
    // Handle widget action
  }
});
```

3. Add schema to `packages/schemas/src/index.ts`:
```typescript
export const MyWidgetSchema = z.object({
  // Define schema
});
```

### Styling

The project uses Tailwind CSS. Key styling patterns:

- **Dark mode**: Supported via `dark:` prefix
- **Responsive**: Mobile-first with `md:`, `lg:` breakpoints
- **Theme colors**: Indigo/purple gradient for primary actions

### Type Safety

TypeScript types are defined in:
- `lib/types.ts`: Frontend-specific types
- `packages/schemas/src/index.ts`: Shared widget schemas

Import shared schemas:
```typescript
import { BalanceCardSchema } from "@ecocash/schemas";
```

## 🔌 API Integration

### CopilotKit Configuration

The frontend connects to the backend via:

1. **Runtime URL**: Configured in `app/api/copilotkit/route.ts`
   - Default: `http://localhost:8000/api/copilotkit`
   - Can be overridden via `REMOTE_ACTION_URL` env var

2. **Agent Name**: `ecocash_agent` (defined in backend)

3. **Streaming**: Enabled by default for real-time responses

### Environment Variables

- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_KEY`: Required for Azure OpenAI API access
- `AZURE_OPENAI_DEPLOYMENT`: Azure OpenAI deployment name (default: gpt-4o-mini)
- `AZURE_OPENAI_API_VERSION`: Azure OpenAI API version (default: 2024-12-01-preview)
- `REMOTE_ACTION_URL`: Backend API endpoint (defaults to localhost:8000)
- `LANGSMITH_API_KEY`: Optional, for LangSmith tracing

## 🎯 Features

### Current Features

1. **Chat Interface**: Full-featured chat UI with CopilotKit
2. **Balance Display**: Real-time balance card widget
3. **Transaction History**: Structured transaction table
4. **Ticket Creation**: Support ticket workflow with confirmation
5. **Responsive Design**: Mobile and desktop support
6. **Dark Mode**: Theme support (via Tailwind)

### Agent Interaction

The frontend communicates with the backend agent through:
- **Messages**: User messages sent to agent
- **Tool Calls**: Agent invokes tools (handled by backend)
- **Widget Rendering**: Agent returns widget data for rendering
- **Streaming**: Real-time response streaming

## 🧪 Testing

### Running Tests

```bash
npm run test
```

### Manual Testing

1. Start backend server (port 8000)
2. Start frontend dev server (port 3000)
3. Open `http://localhost:3000`
4. Test chat interactions:
   - "What's my balance?"
   - "Show me recent transactions"
   - "I need help with a transaction"

## 🚀 Production Build

### Build

```bash
npm run build
```

### Start Production Server

```bash
npm run start
```

### Deploy to Vercel

The project is configured for Vercel deployment:

1. Push to GitHub
2. Import project in Vercel
3. Set environment variables
4. Deploy

## 📦 Dependencies

Key dependencies (see `package.json` for full list):

- `next`: Next.js framework
- `react` & `react-dom`: React library
- `@copilotkit/react-core`: CopilotKit core
- `@copilotkit/react-ui`: CopilotKit UI components
- `@copilotkit/runtime`: CopilotKit runtime
- `tailwindcss`: CSS framework
- `@radix-ui/*`: UI component primitives
- `typescript`: TypeScript compiler

## 🐛 Troubleshooting

### Port Already in Use

If port 3000 is in use:
```bash
npm run dev -- -p 3001
```

### Backend Connection Issues

1. Verify backend is running on port 8000
2. Check `REMOTE_ACTION_URL` in `.env.local`
3. Check browser console for CORS errors
4. Verify backend health endpoint: `http://localhost:8000/`

### Build Errors

1. Clear `.next` directory:
```bash
rm -rf .next
npm run build
```

2. Reinstall dependencies:
```bash
rm -rf node_modules package-lock.json
npm install
```

### Type Errors

Ensure schema package is built:
```bash
cd packages/schemas
npm run build
cd ../..
```

## 📚 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [CopilotKit Documentation](https://docs.copilotkit.ai/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Radix UI Documentation](https://www.radix-ui.com/)
