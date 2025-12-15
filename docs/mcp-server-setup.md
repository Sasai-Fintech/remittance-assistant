# MCP Server Setup Guide

## Overview

The MCP (Model Context Protocol) server is set up as a separate service in a sibling directory to the ecocash-assistant project.

## Location

- **MCP Server Directory**: `/Users/vishnu.kumar/cursorai/mcp-service`
- **Repository**: https://github.com/Sasai-Fintech/mcp-service
- **Status**: External repository (not committed to ecocash-assistant)

## Setup Steps

### 1. Clone Repository (Already Done)

The MCP server has been cloned to:
```
/Users/vishnu.kumar/cursorai/mcp-service
```

### 2. Virtual Environment (Already Set Up)

A Python virtual environment has been created and dependencies installed:
```bash
cd /Users/vishnu.kumar/cursorai/mcp-service
source venv/bin/activate
```

### 3. Environment Configuration

The `.env` file has been created at `/Users/vishnu.kumar/cursorai/mcp-service/.env` with the following configuration:

```bash
# Sasai API Configuration
SASAI_ENVIRONMENT=sandbox
SASAI_USERNAME=your_username_here
SASAI_PASSWORD=your_password_here
SASAI_PIN=your_encrypted_pin_here
SASAI_USER_REFERENCE_ID=your_user_reference_id_here

# MCP HTTP Server Configuration
MCP_HTTP_HOST=0.0.0.0
MCP_HTTP_PORT=8001
MCP_HTTP_PATH=/mcp

# Logging
LOG_LEVEL=INFO
REQUEST_TIMEOUT=30.0
```

**Important**: You need to update the Sasai credentials with actual values:
- `SASAI_USERNAME`: Your Sasai wallet username
- `SASAI_PASSWORD`: Your Sasai wallet password
- `SASAI_PIN`: Your Sasai wallet PIN token
- `SASAI_USER_REFERENCE_ID`: Your Sasai user reference ID

### 4. Running the MCP Server

To start the MCP server with HTTP transport:

```bash
cd /Users/vishnu.kumar/cursorai/mcp-service
source venv/bin/activate
python streamable_http_server.py
```

The server will start on:
- **URL**: `http://localhost:8001/mcp`
- **Host**: `0.0.0.0` (accessible from all interfaces)
- **Port**: `8001` (to avoid conflict with backend on port 8000)
- **Path**: `/mcp`

### 5. Backend Configuration

The backend `.env` file has been updated with:
```bash
MCP_SERVER_URL=http://localhost:8001/mcp
```

This allows the ecocash-assistant backend to connect to the MCP server.

## Available MCP Tools

The MCP server provides the following tools:

### Authentication Tools
- `generate_token` - Generate authentication token using OAuth flow
- `get_token_status` - Check current token availability
- `clear_token` - Clear current authentication token

### Wallet Operation Tools
- `get_wallet_balance` - Retrieve wallet balance for specified currency/provider
- `get_transaction_history` - Get paginated transaction history with filtering
- `get_linked_cards` - Fetch linked payment cards and methods
- `get_airtime_plans` - Browse available airtime and data plans
- `get_customer_profile` - Access customer profile information

### Monitoring Tools
- `health_check` - Comprehensive API health and connectivity check

### Compliance & Knowledge Tools (RAG Integration)
- `wallet_query_compliance_knowledge` - Query Sasai compliance knowledge base
- `wallet_search_compliance_policies` - Search for wallet-specific compliance policies
- `wallet_get_regulatory_guidance` - Get regulatory guidance for wallet operations

## Integration with Backend

The backend will use the `langchain-mcp-adapters` package to load tools from the MCP server:

```python
from langchain_mcp import MCPToolLoader

mcp_tools = MCPToolLoader.load_from_server("http://localhost:8001/mcp")
```

## Troubleshooting

### Server Won't Start
- Check that all required environment variables are set in `.env`
- Verify Python virtual environment is activated
- Check that port 8001 is not already in use

### Connection Errors
- Ensure the MCP server is running before starting the backend
- Verify `MCP_SERVER_URL` in backend `.env` matches the server URL
- Check firewall settings if accessing from remote machines

### Authentication Errors
- Verify Sasai credentials are correct in `.env`
- Check that credentials are not placeholder values
- Ensure network connectivity to Sasai Payment Gateway

## Next Steps

1. Update the `.env` file in `/Users/vishnu.kumar/cursorai/mcp-service/` with actual Sasai credentials
2. Start the MCP server: `python streamable_http_server.py`
3. Verify the server is accessible at `http://localhost:8001/mcp`
4. Integrate MCP tools into the backend using `langchain-mcp-adapters`

