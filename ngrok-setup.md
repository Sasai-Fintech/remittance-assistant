# Ngrok Setup for Frontend Public Access

## Quick Start (Easiest Method)

Use the provided script:

```bash
./start-ngrok.sh
```

This will:
1. Start the frontend dev server (if not already running)
2. Start ngrok tunnel on port 3000
3. Display your public URL

## Manual Setup

1. **Start your frontend dev server** (in one terminal):
   ```bash
   cd frontend
   npm run dev
   ```
   The frontend will run on `http://localhost:3000`

2. **Create ngrok tunnel** (in another terminal):
   ```bash
   ngrok http 3000
   ```

3. **Get your public URL**:
   - ngrok will display a public URL like: `https://abc123.ngrok-free.app`
   - This URL will forward to your local `localhost:3000`
   - Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

## Backend Configuration

**Important**: The frontend needs to connect to your backend. You have two options:

### Option 1: Backend also on ngrok (Recommended)

1. **Start backend** (if not running):
   ```bash
   cd backend
   # Start your backend server on port 8000
   ```

2. **Create ngrok tunnel for backend** (in another terminal):
   ```bash
   ngrok http 8000
   ```
   Copy the HTTPS URL (e.g., `https://xyz789.ngrok-free.app`)

3. **Update frontend environment**:
   Create or update `frontend/.env.local`:
   ```bash
   REMOTE_ACTION_URL=https://xyz789.ngrok-free.app/api/copilotkit
   OPENAI_API_KEY=your_openai_api_key
   ```

4. **Restart frontend** if it's already running

### Option 2: Backend on same machine (localhost)

If your backend is accessible from the same machine, you can use ngrok's request inspection to forward backend requests, or keep backend on localhost and only expose frontend (backend must be accessible from where ngrok runs).

## For Static Domain (Requires ngrok account)

If you have an ngrok account (free tier available):

```bash
# Frontend
ngrok http 3000 --domain=your-frontend.ngrok-free.app

# Backend (separate terminal)
ngrok http 8000 --domain=your-backend.ngrok-free.app
```

## Troubleshooting

- **Port already in use**: Make sure port 3000 is not used by another process
- **Backend connection errors**: Ensure `REMOTE_ACTION_URL` points to your backend ngrok URL
- **CORS issues**: ngrok handles CORS automatically, but check backend CORS settings if needed

## Quick Reference

```bash
# Start frontend + ngrok
./start-ngrok.sh

# Or manually:
cd frontend && npm run dev  # Terminal 1
ngrok http 3000              # Terminal 2

# For backend (if needed):
ngrok http 8000              # Terminal 3
```

