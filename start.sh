#!/bin/bash

# Remittance Assistant - Start Script
# Starts MCP Server, Backend (LangGraph), and Frontend (Next.js)

# Add Poetry to PATH
export PATH="$HOME/.local/bin:$PATH"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to kill background processes on exit
cleanup() {
    echo -e "\n${YELLOW}Stopping services...${NC}"
    kill $(jobs -p) 2>/dev/null
    echo -e "${GREEN}All services stopped.${NC}"
}

trap cleanup EXIT

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Remittance Assistant Startup        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if MCP server should be started
START_MCP=${START_MCP:-true}

if [ "$START_MCP" = "true" ]; then
    echo -e "${BLUE}[1/3] Starting MCP Server...${NC}"
    cd mcp-remittance
    
    # Initialize SASAI_USER_REFERENCE_ID
    SASAI_USER_REFERENCE_ID="(not found)"
    
    # Read MCP_TRANSPORT from .env file if it exists, otherwise use shell env or default
    if [ -f ".env" ]; then
        # Source .env file to get MCP_TRANSPORT
        export $(grep -v '^#' .env | grep MCP_TRANSPORT | xargs) 2>/dev/null || true
        export $(grep -v '^#' .env | grep MCP_HTTP_PORT | xargs) 2>/dev/null || true
        # Read SASAI_USER_REFERENCE_ID for display
        SASAI_USER_REFERENCE_ID=$(grep -v '^#' .env | grep SASAI_USER_REFERENCE_ID | cut -d '=' -f2 | tr -d ' ' | tr -d '"' | tr -d "'") || SASAI_USER_REFERENCE_ID="(not found)"
    fi
    
    # Default to http if not set
    MCP_TRANSPORT=${MCP_TRANSPORT:-http}
    MCP_PORT=${MCP_HTTP_PORT:-8001}
    
    # Check if Python 3.12 is available (required for fastmcp)
    if ! command -v python3.12 &> /dev/null; then
        echo -e "${RED}❌ Error: Python 3.12 is required for MCP server${NC}"
        echo -e "${YELLOW}   fastmcp doesn't support Python 3.14+${NC}"
        echo -e "${YELLOW}   Install: brew install python@3.12${NC}"
        echo -e "${YELLOW}   Or disable: START_MCP=false ./start.sh${NC}"
        cd ..
        exit 1
    fi
    
    # Setup or recreate virtual environment with Python 3.12
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}   Creating virtual environment with Python 3.12...${NC}"
        python3.12 -m venv venv
    else
        # Check if existing venv uses compatible Python version
        source venv/bin/activate
        VENV_PYTHON=$(python --version 2>&1 | grep -oE "3\.[0-9]+")
        deactivate 2>/dev/null || true
        
        if [[ "$VENV_PYTHON" != "3.12" ]] && [[ "$VENV_PYTHON" != "3.11" ]] && [[ "$VENV_PYTHON" != "3.10" ]]; then
            echo -e "${YELLOW}   Recreating venv with Python 3.12 (found Python $VENV_PYTHON)...${NC}"
            rm -rf venv
            python3.12 -m venv venv
        fi
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check if dependencies are installed (check for fastmcp)
    if ! python -c "import fastmcp" 2>/dev/null; then
        echo -e "${YELLOW}   Installing MCP dependencies...${NC}"
        pip install -q --upgrade pip
        pip install -q -r requirements.txt
    fi
    
    # Use python from venv (should now be 3.10-3.12)
    PYTHON_CMD="python"
    
    # Start MCP server using server.py (automatically uses HTTP transport from .env)
    $PYTHON_CMD server.py &
    MCP_PID=$!
    
    # Display startup message based on transport
    if [ "$MCP_TRANSPORT" != "stdio" ]; then
        echo -e "${GREEN}✅ MCP Server starting on http://localhost:${MCP_PORT}/mcp${NC}"
        echo -e "   Transport: ${MCP_TRANSPORT}"
    else
        echo -e "${GREEN}✅ MCP Server starting with STDIO transport${NC}"
    fi
    echo -e "   User ID: ${SASAI_USER_REFERENCE_ID}"
    echo ""
    
    cd ..
    sleep 3
else
    echo -e "${YELLOW}⚠️  MCP Server disabled (START_MCP=false)${NC}"
    echo ""
fi

# Start Backend
echo -e "${BLUE}[2/3] Starting Backend (LangGraph + FastAPI)...${NC}"
cd backend

# Check if poetry or uv is available, otherwise try pip
if command -v poetry &> /dev/null; then
    # Install dependencies if not already installed
    if [ ! -d ".venv" ] && [ ! -f ".venv/bin/activate" ]; then
        echo -e "${YELLOW}   Installing backend dependencies with Poetry...${NC}"
        poetry install --no-interaction
    fi
    poetry run uvicorn app.main:app --reload --port 8000 &
    BACKEND_PID=$!
    echo -e "${GREEN}✅ Backend starting on http://localhost:8000${NC}"
elif command -v uv &> /dev/null; then
    echo -e "${YELLOW}   Using uv to run backend...${NC}"
    uv run uvicorn app.main:app --reload --port 8000 &
    BACKEND_PID=$!
    echo -e "${GREEN}✅ Backend starting on http://localhost:8000${NC}"
else
    echo -e "${RED}⚠️  Warning: Could not start backend. Poetry or uv not found.${NC}"
    echo -e "${YELLOW}   Install Poetry: curl -sSL https://install.python-poetry.org | python3 -${NC}"
    echo -e "${YELLOW}   Or install uv: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    cd ..
    exit 1
fi
echo ""

cd ..

# Wait for backend to be ready
sleep 5

# Start Frontend
echo -e "${BLUE}[3/3] Starting Frontend (Next.js)...${NC}"
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}   Installing frontend dependencies...${NC}"
    if command -v pnpm &> /dev/null; then
        pnpm install
    elif command -v npm &> /dev/null; then
        npm install
    else
        echo -e "${RED}⚠️  Error: npm or pnpm not found. Install Node.js first.${NC}"
        cd ..
        exit 1
    fi
fi

# Start frontend
if command -v pnpm &> /dev/null; then
    pnpm dev &
elif command -v npm &> /dev/null; then
    npm run dev &
else
    echo -e "${RED}⚠️  Error: npm or pnpm not found. Install Node.js first.${NC}"
    cd ..
    exit 1
fi

FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend starting on http://localhost:3000${NC}"
echo ""

cd ..

# Display summary
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   All Services Started! 🚀            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
if [ "$START_MCP" = "true" ]; then
    echo -e "${BLUE}📡 MCP Server:${NC}   http://localhost:${MCP_PORT}/mcp (${MCP_TRANSPORT})"
fi
echo -e "${BLUE}🔧 Backend API:${NC}  http://localhost:8000"
echo -e "${BLUE}🌐 Frontend:${NC}     http://localhost:3000"
echo ""
echo -e "${YELLOW}📖 Documentation:${NC}"
echo -e "   - Quick Start:  ${PWD}/QUICK_START_GUIDE.md"
echo -e "   - User Journey: ${PWD}/REMITTANCE_USER_JOURNEY.md"
echo -e "   - Summary:      ${PWD}/REMITTANCE_IMPLEMENTATION_SUMMARY.md"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services.${NC}"
echo ""

wait
