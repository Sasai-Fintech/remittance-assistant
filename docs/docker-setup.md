# Docker Setup Guide

This guide explains how to run the EcoCash Assistant using Docker and Docker Compose.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose v3.8 or later

## Quick Start

1. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start all services**:
   ```bash
   docker-compose up -d
   ```

3. **View logs**:
   ```bash
   docker-compose logs -f
   ```

4. **Stop services**:
   ```bash
   docker-compose down
   ```

## Services

### Backend (port 8000)
- FastAPI application
- Connects to MongoDB for session persistence
- Health check: `http://localhost:8000/`
- Requires `MONGODB_URI` environment variable

### Frontend (port 3000)
- Next.js application
- Connects to backend API
- Health check: `http://localhost:3000/api/health`

## Environment Variables

Create a `.env` file in the root directory:

```bash
# MongoDB (use MongoDB Atlas or local MongoDB)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=ecocash_assistant

# Or for local MongoDB:
# MONGODB_URI=mongodb://localhost:27017
# MONGODB_DB_NAME=ecocash_assistant

# Backend
OPENAI_API_KEY=your_openai_api_key

# Frontend (optional, defaults work for local dev)
NEXT_PUBLIC_REMOTE_ACTION_URL=http://localhost:8000/api/copilotkit
```

## Development Workflow

### Rebuild after code changes:
```bash
docker-compose up -d --build
```

### View specific service logs:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart a specific service:
```bash
docker-compose restart backend
```

## Database Management

### MongoDB Collections:
The checkpointer automatically creates the `checkpoints` collection on first use.

### Backup MongoDB (if using local MongoDB):
```bash
# Using mongodump
mongodump --uri="mongodb://localhost:27017" --db=ecocash_assistant --out=./backup
```

### Restore MongoDB (if using local MongoDB):
```bash
# Using mongorestore
mongorestore --uri="mongodb://localhost:27017" --db=ecocash_assistant ./backup/ecocash_assistant
```

### Access MongoDB (if using local MongoDB):
```bash
# Using mongosh
mongosh "mongodb://localhost:27017/ecocash_assistant"
```

## Troubleshooting

### Services won't start:
1. Check if ports 3000, 8000 are available
2. Verify Docker has enough resources allocated
3. Check logs: `docker-compose logs`

### Database connection errors:
1. Verify MongoDB is accessible (check MongoDB Atlas or local MongoDB)
2. Check connection string in backend logs
3. Verify `MONGODB_URI` is set correctly
4. For MongoDB Atlas, ensure IP whitelist includes your IP

### Frontend can't connect to backend:
1. Check `NEXT_PUBLIC_REMOTE_ACTION_URL` environment variable
2. Verify backend is running: `curl http://localhost:8000/`
3. Check network: `docker-compose network ls`

### Health checks failing:
1. Wait for services to fully start (40s start period)
2. Check service logs for errors
3. Verify endpoints are accessible

## Production Considerations

For production deployment:
1. Use MongoDB Atlas (managed, scalable MongoDB)
2. Use strong passwords and enable authentication
3. Set up proper networking and IP whitelisting
4. Use environment-specific `.env` files
5. Configure resource limits in `docker-compose.yml`
6. Set up MongoDB backups for session data
7. Use Azure Container Apps or similar for orchestration

## Clean Up

### Remove all containers and volumes:
```bash
docker-compose down -v
```

### Remove images:
```bash
docker-compose down --rmi all
```

