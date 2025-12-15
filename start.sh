#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping services..."
    kill $(jobs -p) 2>/dev/null
}

trap cleanup EXIT

echo "Starting Ecocash Assistant..."

# Check if MCP server should be started
START_MCP=${START_MCP:-true}

if [ "$START_MCP" = "true" ]; then
    # Start MCP Server (optional - can be disabled with START_MCP=false)
    # Transport mode is configured via MCP_TRANSPORT in mcp-ecocash/.env file
    echo "Starting MCP Server..."
    cd mcp-ecocash
    
    # Initialize SASAI_USER_REFERENCE_ID
    SASAI_USER_REFERENCE_ID="(not found)"
    
    # Read MCP_TRANSPORT from .env file if it exists, otherwise use shell env or default
    if [ -f ".env" ]; then
        # Source .env file to get MCP_TRANSPORT (simple approach)
        export $(grep -v '^#' .env | grep MCP_TRANSPORT | xargs) 2>/dev/null || true
        export $(grep -v '^#' .env | grep MCP_HTTP_PORT | xargs) 2>/dev/null || true
        # Read SASAI_USER_REFERENCE_ID for display
        SASAI_USER_REFERENCE_ID=$(grep -v '^#' .env | grep SASAI_USER_REFERENCE_ID | cut -d '=' -f2 | tr -d ' ' | tr -d '"' | tr -d "'") || SASAI_USER_REFERENCE_ID="(not found)"
    fi
    
    # Default to http if not set
    MCP_TRANSPORT=${MCP_TRANSPORT:-http}
    MCP_PORT=${MCP_HTTP_PORT:-8001}
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        python server.py &
        MCP_PID=$!
    elif command -v python3.12 &> /dev/null; then
        python3.12 server.py &
        MCP_PID=$!
    elif command -v python3 &> /dev/null; then
        python3 server.py &
        MCP_PID=$!
    else
        echo "⚠️  Warning: Could not start MCP server. Make sure Python 3.12+ is installed and MCP server dependencies are set up."
        echo "   You can disable MCP server by setting START_MCP=false"
        cd ..
        exit 1
    fi
    
    # Display startup message based on transport
    if [ "$MCP_TRANSPORT" != "stdio" ]; then
        echo "✅ MCP Server starting on http://localhost:${MCP_PORT}/mcp (transport: ${MCP_TRANSPORT})"
    else
        echo "✅ MCP Server starting with STDIO transport"
    fi
    echo "   Using SASAI_USER_REFERENCE_ID: ${SASAI_USER_REFERENCE_ID}"
    
    cd ..
    sleep 3
fi

# Start Backend
echo "Starting Backend (FastAPI)..."
cd backend
poetry run uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready (simple sleep for now)
sleep 5

# Start Frontend
echo "Starting Frontend (Next.js)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Services started!"
if [ "$START_MCP" = "true" ]; then
    echo "MCP Server: http://localhost:8001/mcp"
fi
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop."

wait
