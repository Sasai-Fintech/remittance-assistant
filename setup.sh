#!/bin/bash

# Remittance Assistant - Setup Script
# Installs all dependencies for MCP Server, Backend, and Frontend

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Remittance Assistant Setup          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Check Python version
echo -e "${BLUE}[1/4] Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo -e "${GREEN}✅ Python ${PYTHON_VERSION} found${NC}"
else
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

# Setup MCP Server
echo -e "\n${BLUE}[2/4] Setting up MCP Server...${NC}"
cd mcp-remittance

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}   Creating virtual environment...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate
echo -e "${YELLOW}   Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
deactivate

echo -e "${GREEN}✅ MCP Server setup complete${NC}"
cd ..

# Setup Backend
echo -e "\n${BLUE}[3/4] Setting up Backend...${NC}"
cd backend

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${YELLOW}   Poetry not found. Installing Poetry...${NC}"
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

if command -v poetry &> /dev/null; then
    echo -e "${YELLOW}   Installing dependencies with Poetry...${NC}"
    poetry install --no-interaction
    echo -e "${GREEN}✅ Backend setup complete${NC}"
else
    echo -e "${YELLOW}   Poetry installation requires shell restart${NC}"
    echo -e "${YELLOW}   Please run: export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
    echo -e "${YELLOW}   Then run this setup script again${NC}"
fi

cd ..

# Setup Frontend
echo -e "\n${BLUE}[4/4] Setting up Frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}   Installing dependencies...${NC}"
    if command -v pnpm &> /dev/null; then
        pnpm install
    elif command -v npm &> /dev/null; then
        npm install
    else
        echo -e "${RED}❌ npm or pnpm not found. Please install Node.js 18+${NC}"
        cd ..
        exit 1
    fi
else
    echo -e "${GREEN}✅ Dependencies already installed${NC}"
fi

echo -e "${GREEN}✅ Frontend setup complete${NC}"
cd ..

# Summary
echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Setup Complete! 🎉                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Run: ${BLUE}./start.sh${NC}"
echo -e "  2. Open: ${BLUE}http://localhost:3000${NC}"
echo ""
echo -e "${YELLOW}Documentation:${NC}"
echo -e "  - ${PWD}/QUICK_START_GUIDE.md"
echo -e "  - ${PWD}/REMITTANCE_USER_JOURNEY.md"
echo ""
