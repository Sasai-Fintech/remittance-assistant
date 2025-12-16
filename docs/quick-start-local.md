# Quick Start: Local MongoDB Setup

## ✅ MongoDB Configuration

The Ecocash Assistant uses MongoDB to persist chat sessions. You can use either:
- **MongoDB Atlas** (cloud, recommended) - Already configured in the project
- **Local MongoDB** - For local development

## Step 1: Configure Backend Connection

Create or update `backend/.env` file:

```bash
# Option 1: Use MongoDB Atlas (recommended - already configured)
MONGODB_URI=mongodb+srv://sasairagengine:j3ugUjql4I60TY52@sandbox.detzo.mongodb.net/?retryWrites=true&w=majority&appName=sandbox
MONGODB_DB_NAME=remittance_assistant

# Option 2: Use Local MongoDB
# MONGODB_URI=mongodb://localhost:27017
# MONGODB_DB_NAME=remittance_assistant

# Your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
```

**Note**: The project already has MongoDB Atlas configured. You can use the existing connection string or set up your own.

## Step 2: Verify Connection

Test the MongoDB connection:

```bash
# Using MongoDB Shell (mongosh)
mongosh "your_mongodb_uri"

# Or test via backend debug endpoint (after starting backend)
curl http://localhost:8000/api/sessions/debug
```

## Step 3: Restart Backend

If your backend is already running, restart it to pick up the new MongoDB connection:

1. Stop the backend (Ctrl+C in the terminal)
2. Start it again: `cd backend && poetry run uvicorn app.main:app --reload --port 8000`

The backend will automatically:
- Connect to MongoDB if `MONGODB_URI` is set
- Fall back to MemorySaver if MongoDB is unavailable
- Log connection status on startup

## Step 4: Test Session Persistence

1. Start a conversation in the frontend
2. Send a few messages
3. Restart the backend server
4. Continue the conversation - it should remember previous messages!

## Verify It's Working

Check backend logs for:
```
✅ Using MongoDBSaver for session persistence (database: remittance_assistant)
```
Or if MongoDB is unavailable:
```
⚠️ MONGODB_URI not set. Using MemorySaver (sessions will not persist).
```

Check database has checkpoints:
```bash
# Using MongoDB Shell
mongosh "your_mongodb_uri"
use remittance_assistant
db.checkpoints.countDocuments({})

# Or use the debug API endpoint
curl http://localhost:8000/api/sessions/debug
```

## Troubleshooting

### Backend can't connect
- Verify MongoDB is running (if using local): `brew services list` or `docker ps`
- Check connection string in `backend/.env`
- Check backend logs for error messages
- For MongoDB Atlas, verify IP whitelist includes your IP

### MongoDB not installed locally
If you want to use local MongoDB:
```bash
# macOS
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# Or use Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### Connection timeout
- Check firewall rules
- Verify MongoDB Atlas IP whitelist
- Ensure connection string is correct

## Next Steps

Once local testing is complete, you can:
1. Use MongoDB Atlas for production (already configured)
2. Deploy to Azure: Follow `azure-deploy.md`
3. See `mongodb-setup.md` for detailed MongoDB setup instructions

