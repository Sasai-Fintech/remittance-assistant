#!/bin/bash

# Script to start frontend dev server and expose it via ngrok

echo "🚀 Starting Frontend with ngrok tunnel..."

# Check if frontend dev server is already running
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Frontend dev server is already running on port 3000"
else
    echo "📦 Starting frontend dev server..."
    cd frontend
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"
    cd ..
    
    # Wait for server to be ready
    echo "⏳ Waiting for frontend to be ready..."
    sleep 8
fi

# Check if ngrok is already running
if pgrep -x "ngrok" > /dev/null; then
    echo "⚠️  ngrok is already running. Please stop it first or use the existing tunnel."
    echo "   To stop: pkill ngrok"
    exit 1
fi

# Start ngrok
echo "🌐 Starting ngrok tunnel on port 3000..."
echo ""
echo "=========================================="
echo "  Your public URL will be displayed below"
echo "=========================================="
echo ""

ngrok http 3000

