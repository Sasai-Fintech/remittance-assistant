# MongoDB Setup Guide

This guide helps you set up MongoDB for chat session persistence in the Ecocash Assistant.

## Overview

The Ecocash Assistant uses MongoDB to persist chat sessions, ensuring all conversations are saved and can be retrieved like ChatGPT. Sessions are stored in MongoDB using LangGraph's `MongoDBSaver` checkpointer.

## Quick Setup

### Option 1: Use Existing MongoDB Atlas (Recommended)

If you already have MongoDB Atlas configured (as used in mcp-remittance), you can reuse the same connection:

1. **Get MongoDB URI** from your existing configuration or MongoDB Atlas dashboard
2. **Set environment variables** in `backend/.env`:

```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=remittance_assistant
OPENAI_API_KEY=your_openai_api_key
```

### Option 2: Local MongoDB Setup

#### 1. Install MongoDB

**macOS (using Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

**Docker:**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

#### 2. Configure Backend

Create or update `backend/.env`:

```bash
# Local MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=remittance_assistant

# Or MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=remittance_assistant

OPENAI_API_KEY=your_openai_api_key
```

## Verify Setup

### Test MongoDB Connection

**Using MongoDB Shell:**
```bash
# Connect to local MongoDB
mongosh

# Or connect to MongoDB Atlas
mongosh "mongodb+srv://username:password@cluster.mongodb.net/remittance_assistant"
```

**Test connection:**
```javascript
// In mongosh
use remittance_assistant
db.runCommand({ ping: 1 })
```

### Test Backend Connection

1. Start the backend server
2. Check backend logs for:
   ```
   ✅ Using MongoDBSaver for session persistence (database: remittance_assistant)
   ```
3. If MongoDB is unavailable, you'll see:
   ```
   ⚠️ MONGODB_URI not set. Using MemorySaver (sessions will not persist).
   ```

### Verify Sessions Are Being Saved

1. Start a conversation in the frontend
2. Send a few messages
3. Check MongoDB for checkpoints:

```javascript
// In mongosh
use remittance_assistant
db.checkpoints.countDocuments({})
db.checkpoints.find().limit(1).pretty()
```

Or using the debug endpoint:
```bash
curl http://localhost:8000/api/sessions/debug
```

## Testing Session Persistence

1. Start a conversation in the frontend
2. Send a few messages
3. Restart the backend server
4. Continue the conversation - it should remember previous messages!
5. Check sessions via API:

```bash
# List all sessions
curl http://localhost:8000/api/sessions/

# Get specific session
curl http://localhost:8000/api/sessions/{thread_id}
```

## MongoDB Collections

The checkpointer automatically creates the following collections:

- **`checkpoints`**: Stores all conversation checkpoints (session state)
  - `thread_id`: Unique identifier for each chat session
  - `checkpoint_ns`: Namespace (usually empty string)
  - `checkpoint_id`: Unique checkpoint identifier
  - `checkpoint`: The actual state data

## Connection Strings

### Local MongoDB (default)
```
mongodb://localhost:27017
```

### Local MongoDB (with authentication)
```
mongodb://username:password@localhost:27017
```

### MongoDB Atlas
```
mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

### MongoDB Atlas (with database name in URI)
```
mongodb+srv://username:password@cluster.mongodb.net/remittance_assistant?retryWrites=true&w=majority
```

## Troubleshooting

### Backend Can't Connect to MongoDB

1. **Verify MongoDB is running:**
   ```bash
   # macOS
   brew services list
   
   # Linux
   sudo systemctl status mongodb
   
   # Docker
   docker ps | grep mongodb
   ```

2. **Check connection string** in `backend/.env`
3. **Test connection manually:**
   ```bash
   mongosh "your_mongodb_uri"
   ```

4. **Check backend logs** for detailed error messages

### Connection Timeout

- Verify MongoDB is accessible from your network
- Check firewall rules (for MongoDB Atlas, whitelist your IP)
- Ensure connection string is correct

### Authentication Errors

- Verify username and password in connection string
- For MongoDB Atlas, ensure database user has proper permissions
- Check if IP whitelist includes your current IP

### Sessions Not Persisting

1. Check backend logs for MongoDB connection status
2. Verify `MONGODB_URI` is set correctly
3. Test MongoDB connection directly
4. Check if `checkpoints` collection exists:
   ```javascript
   use remittance_assistant
   show collections
   ```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGODB_URI` | MongoDB connection string | - | Yes (for persistence) |
| `MONGODB_DB_NAME` | Database name for sessions | `remittance_assistant` | No |

## Production Considerations

1. **Use MongoDB Atlas** for production (managed, scalable)
2. **Enable authentication** and use strong passwords
3. **Configure IP whitelist** for security
4. **Set up backups** for session data
5. **Monitor collection size** and implement cleanup for old sessions if needed
6. **Use connection pooling** (handled automatically by Motor)

## Next Steps

- Test session persistence locally
- Deploy to production with MongoDB Atlas
- Monitor session storage usage
- Implement session cleanup policies if needed

