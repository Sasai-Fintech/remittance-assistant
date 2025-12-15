#!/usr/bin/env bash
set -euo pipefail
# ------------------------------------------------------------
# 1️⃣  Stop any running dev servers (uvicorn & npm dev)
# ------------------------------------------------------------
echo "🔴 Stopping any running backend/frontend processes..."
pkill -f uvicorn || true
pkill -f "npm run dev" || true
sleep 2
# ------------------------------------------------------------
# 2️⃣  Back‑up current Ecocash‑Assistant code
# ------------------------------------------------------------
PROJECT_ROOT="/Users/vishnu.kumar/cursorai/ecocash-assistant"
echo "📦 Back‑up existing backend & frontend..."
mv "${PROJECT_ROOT}/backend/agent"          "${PROJECT_ROOT}/backend/agent_backup"
mv "${PROJECT_ROOT}/frontend/app"           "${PROJECT_ROOT}/frontend/app_backup"
# ------------------------------------------------------------
# 3️⃣  Copy the travel‑example code into the project
# ------------------------------------------------------------
TRAVEL_SRC="/tmp/copilotkit-reference/examples/coagents-travel"
echo "📂 Copying travel‑example backend files..."
cp -R "${TRAVEL_SRC}/agent/." "${PROJECT_ROOT}/backend/"
echo "📂 Copying travel‑example frontend files..."
cp -R "${TRAVEL_SRC}/ui/." "${PROJECT_ROOT}/frontend/"
# ------------------------------------------------------------
# 4️⃣  Rename the agent to `ecocash_agent`
# ------------------------------------------------------------
# Backend graph (agent name is defined here)
GRAPH_FILE="${PROJECT_ROOT}/backend/agent/graph.py"
if [[ -f "${GRAPH_FILE}" ]]; then
  echo "🔧 Updating agent name in ${GRAPH_FILE} ..."
  sed -i '' 's/name="travel"/name="ecocash_agent"/' "${GRAPH_FILE}"
fi
# FastAPI entry point (LangGraphAgent definition)
MAIN_PY="${PROJECT_ROOT}/backend/app/main.py"
if [[ -f "${MAIN_PY}" ]]; then
  echo "🔧 Updating agent name in ${MAIN_PY} ..."
  sed -i '' 's/name="travel"/name="ecocash_agent"/' "${MAIN_PY}"
fi
# Front‑end page (CopilotKit wrapper)
PAGE_TSX="${PROJECT_ROOT}/frontend/app/page.tsx"
if [[ -f "${PAGE_TSX}" ]]; then
  echo "🔧 Updating CopilotKit prop in ${PAGE_TSX} ..."
  # Ensure the `agent=` prop exists and is set to ecocash_agent
  if grep -q 'agent=' "${PAGE_TSX}"; then
    sed -i '' 's/agent="[^"]*"/agent="ecocash_agent"/' "${PAGE_TSX}"
  else
    # If the prop is missing, insert it after `<CopilotKit`
    sed -i '' '/<CopilotKit/a\  agent="ecocash_agent"' "${PAGE_TSX}"
  fi
fi
# ------------------------------------------------------------
# 5️⃣  Install dependencies
# ------------------------------------------------------------
echo "📦 Installing Python dependencies (backend)…"
cd "${PROJECT_ROOT}/backend"
poetry install
echo "📦 Installing Node dependencies (frontend)…"
cd "${PROJECT_ROOT}/frontend"
npm install
# ------------------------------------------------------------
# 6️⃣  Run the new application
# ------------------------------------------------------------
echo "🚀 Starting backend (uvicorn)…"
# Run in background so the script can continue; you can also run it manually later.
cd "${PROJECT_ROOT}/backend"
poetry run uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
echo "🚀 Starting frontend (Next.js dev server)…"
cd "${PROJECT_ROOT}/frontend"
npm run dev
# ------------------------------------------------------------
# 7️⃣  Done!
# ------------------------------------------------------------
echo "✅ Travel example is now the main Ecocash Assistant code."
echo "   • Backend: http://localhost:8000"
echo "   • Frontend: http://localhost:3000"
