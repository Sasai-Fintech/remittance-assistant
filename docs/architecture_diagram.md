# Ecocash Assistant: System Architecture

This document provides a high-level architectural view of the Ecocash Assistant, designed for technical leadership. It illustrates the component interactions, data flow, and the integration of the Agentic Workflow Engine (LangGraph) with the Model Context Protocol (MCP).

## System Context Diagram

The system is composed of three primary layers:
1.  **Presentation Layer (Frontend)**: A Next.js application providing the chat interface and interactive financial widgets.
2.  **Orchestration Layer (Backend)**: A FastAPI service hosting the LangGraph agent, managing state, intent detection, and workflow routing.
3.  **Capability Layer (MCP Server)**: A dedicated service exposing financial tools and integrations via the Model Context Protocol.

```mermaid
graph TD
    %% Styles
    classDef frontend fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000;
    classDef backend fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000;
    classDef mcp fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000;
    classDef external fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000;
    classDef database fill:#eceff1,stroke:#455a64,stroke-width:2px,stroke-dasharray: 5 5,color:#000;

    subgraph Client_Device [User Device]
        Browser[Web Browser / Mobile App]:::frontend
    end

    subgraph Frontend_Service [Frontend Service - Next.js]
        UI_Components[UI Components\n(Chat, Widgets, History)]:::frontend
        CopilotKit_Client[CopilotKit Client SDK\n(Hooks, State, Suggestions)]:::frontend
        Next_API[Next.js API Routes\n(/api/copilotkit)]:::frontend
    end

    subgraph Backend_Service [Backend Service - FastAPI + LangGraph]
        API_Endpoint[FastAPI Endpoint\n(/api/copilotkit)]:::backend
        
        subgraph Agent_Engine [LangGraph Agent Engine]
            direction TB
            Intent_Node[Intent Detection Node]:::backend
            Chat_Node[Chat Node\n(General Conversation)]:::backend
            
            subgraph Workflows [Specialized Workflows]
                Txn_Help[Transaction Help Graph]:::backend
                Insights[Financial Insights Graph]:::backend
                Refund[Refund Graph]:::backend
                Loan[Loan Enquiry Graph]:::backend
            end
            
            Router[Workflow Router]:::backend
            HITL[Human-in-the-Loop\n(Ticket Confirmation)]:::backend
        end
        
        MCP_Client[MCP Client Utility]:::backend
    end

    subgraph MCP_Service [MCP Server - mcp-remittance]
        MCP_Server[FastMCP Server]:::mcp
        
        subgraph Tools [Tool Capabilities]
            Wallet_Tools[Wallet Tools\n(Balance, Transactions)]:::mcp
            Insight_Tools[Insight Tools\n(Cash Flow, Spending)]:::mcp
            Support_Tools[Support Tools\n(Create Ticket)]:::mcp
        end
    end

    subgraph External_Services [External Infrastructure]
        LLM[OpenAI LLM\n(GPT-4o-mini)]:::external
        DB[(MongoDB\nSession Persistence)]:::database
    end

    %% Data Flow Connections
    Browser <-->|"HTTPS / WebSocket"| UI_Components
    UI_Components <-->|"React Context"| CopilotKit_Client
    CopilotKit_Client <-->|"HTTP POST"| Next_API
    Next_API <-->|"HTTP Proxy"| API_Endpoint
    
    API_Endpoint --> Agent_Engine
    
    %% Agent Flow
    Agent_Engine <-->|"State Persistence"| DB
    Agent_Engine <-->|"Inference API"| LLM
    
    %% Internal Agent Routing
    Intent_Node --> Router
    Router --> Chat_Node
    Router --> Workflows
    Workflows --> Chat_Node
    Chat_Node --> HITL
    
    %% MCP Integration
    Chat_Node -- "Tool Calls" --> MCP_Client
    MCP_Client <-->|"SSE (Server-Sent Events)"| MCP_Server
    MCP_Server --> Tools

    %% Legend
    linkStyle default stroke:#333,stroke-width:1px;
```

## Key Capabilities & Data Flow

### 1. Presentation Layer (Frontend)
*   **Technology**: Next.js, React, TailwindCSS, CopilotKit UI.
*   **Role**: Renders the chat interface and "Generative UI" widgets (e.g., Transaction Tables, Insight Charts).
*   **Data Flow**: Captures user input and renders streaming responses from the backend. It uses `useCopilotChatSuggestions` to generate context-aware next steps locally or via the agent.

### 2. Orchestration Layer (Backend)
*   **Technology**: Python, FastAPI, LangGraph, LangChain.
*   **Role**: The "Brain" of the assistant. It maintains conversation state and orchestrates the logic.
*   **Graph Logic**:
    *   **Intent Detection**: Analyzes the user's first message to route them to a specialized subgraph (e.g., "Help with transaction" -> `Transaction Help Graph`).
    *   **Subgraphs**: Isolated state machines for complex tasks (e.g., collecting transaction details, verifying refund eligibility).
    *   **Chat Node**: Handles general conversation and tool execution.
    *   **Human-in-the-Loop**: Pauses execution for critical actions (e.g., `Ticket Confirmation`) requiring explicit user approval.

### 3. Capability Layer (MCP Server)
*   **Technology**: Python, `mcp` SDK (FastMCP).
*   **Role**: Provides deterministic tools to the agent. This decouples the "Brain" (Backend) from the "Hands" (Tools).
*   **Tools**:
    *   `get_wallet_balance`: Fetches real-time balance.
    *   `get_wallet_transaction_history`: Retrieves transaction logs.
    *   `create_ticket`: Submits support tickets (after confirmation).
    *   `get_financial_insights`: Aggregates data for visualization.

### 4. Persistence & Intelligence
*   **MongoDB**: Stores the LangGraph `Checkpoint` state, allowing conversations to persist across sessions and enabling "time travel" debugging. Uses MongoDB Atlas for managed, scalable storage.
*   **OpenAI**: Provides the reasoning capabilities for intent detection, response generation, and tool selection.
