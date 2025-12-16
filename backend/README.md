# Remittance Assistant Backend

FastAPI backend server with LangGraph agent for the Remittance AI Assistant. The backend provides a conversational AI agent that helps users manage their wallet, view transactions, and create support tickets.

## 🏗️ Architecture

The backend is built with:

- **FastAPI**: Web framework for the API server
- **LangGraph**: Agent orchestration and workflow management
- **CopilotKit**: Integration with AG-UI protocol for rich widget rendering
- **Azure OpenAI GPT-4o-mini**: LLM for natural language understanding
- **Poetry**: Python dependency management

## 📋 Prerequisites

- Python 3.12 (strictly required - see `pyproject.toml`)
- Poetry installed (`pip install poetry`)

## 🚀 Setup

### 1. Install Dependencies

```bash
poetry install
```

This will install all dependencies specified in `pyproject.toml`.

### 2. Environment Configuration

Create a `.env` file in the `backend/` directory:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://azureopenai-uswest-sandbox.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

**Note**: The `.env` file is gitignored and should never be committed.

### 3. Run the Server

```bash
poetry run uvicorn app.main:app --reload --port 8000
```

The server will start on `http://localhost:8000`.

### Alternative: Using Poetry Script

```bash
poetry run demo
```

## 📁 Project Structure

```
backend/
├── agent/                  # LangGraph agent definition
│   ├── graph.py           # Agent workflow graph builder
│   └── tools.py           # Agent tool definitions (placeholders)
├── app/                    # FastAPI application
│   └── main.py            # FastAPI entry point and CopilotKit integration
├── engine/                 # Agent engine components
│   ├── chat.py            # Chat node implementation
│   └── state.py           # Agent state type definitions
├── mcp/                    # MCP tools (Model Context Protocol)
│   └── tools.py           # MCP tool implementations
├── static/                 # Static assets
│   └── agent-diagram.png  # Agent workflow diagram
├── langgraph.json         # LangGraph CLI configuration
└── pyproject.toml         # Poetry dependencies and project config
```

## 🔧 Agent Architecture

### Graph Structure

The agent uses LangGraph with the following structure:

```
START → chat_node → [route decision]
                      ├─→ remittance_tools (if tools called)
                      └─→ END (if no tools)
```

### Nodes

1. **chat_node** (`engine/chat.py`):
   - Handles user messages
   - Uses Azure OpenAI GPT-4o-mini with tool binding
   - Returns AI responses with optional tool calls

2. **remittance_tools** (ToolNode):
   - Executes agent tools when called
   - Tools: `get_balance`, `list_transactions`, `create_ticket`

### State

The agent state (`engine/state.py`) extends `MessagesState` from LangGraph and includes:
- `messages`: Conversation history
- Additional state fields for future extensions

### Tools

Current tools (defined in `agent/tools.py`):

- **get_balance(user_id: str)**: Returns wallet balance (placeholder)
- **list_transactions(user_id: str, limit: int)**: Returns transaction list (placeholder)
- **create_ticket(user_id: str, subject: str, body: str)**: Creates support ticket (placeholder)

**Note**: These are placeholder implementations. In production, they should connect to real APIs or MCP servers.

## 🔌 API Endpoints

### CopilotKit Endpoint

- **POST** `/api/copilotkit`: Main CopilotKit runtime endpoint
  - Handles chat messages from the frontend
  - Processes through LangGraph agent
  - Returns streaming responses

### Health Check

- **GET** `/`: Health check endpoint
  - Returns: `{"message": "Remittance Assistant Backend is running"}`

## 🧪 Development

### Running in Development Mode

```bash
poetry run uvicorn app.main:app --reload --port 8000
```

The `--reload` flag enables auto-reload on code changes.

### Adding New Tools

1. Define the tool in `agent/tools.py`:
```python
from langchain.tools import tool

@tool
def my_new_tool(param: str) -> str:
    """Tool description for the LLM."""
    # Implementation
    return "result"
```

2. Import and add to the graph in `agent/graph.py`:
```python
from agent.tools import my_new_tool

graph_builder.add_node("remittance_tools", ToolNode([
    get_balance, 
    list_transactions, 
    create_ticket,
    my_new_tool  # Add here
]))
```

3. Bind to LLM in `engine/chat.py`:
```python
llm_with_tools = llm.bind_tools(
    [get_balance, list_transactions, create_ticket, my_new_tool],
    parallel_tool_calls=False,
)
```

### Modifying Agent Behavior

Edit the system message in `engine/chat.py` to change agent behavior:

```python
system_message = """
You are the Remittance Assistant...
[Modify instructions here]
"""
```

## 🔐 Security Considerations

- **API Keys**: Never commit `.env` files
- **JWT Validation**: Currently not implemented (MVP). Add JWT validation middleware for production
- **Rate Limiting**: Should be added for production deployments
- **Input Validation**: Add Pydantic models for request validation

## 📊 Observability

Currently, the backend uses basic logging. For production, consider:

- Structured logging with request IDs
- OpenTelemetry integration
- Metrics collection (tool call latency, success rates)
- Error tracking (Sentry, etc.)

## 🚀 Production Deployment

### Using LangGraph Cloud

The `langgraph.json` file is configured for LangGraph Cloud deployment:

```json
{
    "python_version": "3.12",
    "dependencies": ["."],
    "graphs": {
        "travel": "./travel/agent.py:graph"
    },
    "env": ".env"
}
```

**Note**: Update the graph path if your structure differs.

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev
COPY . .
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📝 Dependencies

Key dependencies (see `pyproject.toml` for full list):

- `fastapi`: Web framework
- `langgraph`: Agent orchestration
- `langchain-openai`: OpenAI integration
- `copilotkit`: CopilotKit integration
- `uvicorn`: ASGI server
- `python-dotenv`: Environment variable management

## 🐛 Troubleshooting

### Python Version Issues

Ensure you're using Python 3.12:
```bash
python --version  # Should show 3.12.x
poetry env use python3.12
```

### Port Already in Use

If port 8000 is in use:
```bash
poetry run uvicorn app.main:app --reload --port 8001
```

Update `frontend/.env.local` to point to the new port.

### Import Errors

Ensure all dependencies are installed:
```bash
poetry install
```

## 📚 Additional Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [CopilotKit Documentation](https://docs.copilotkit.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
