# Local PostgreSQL Setup Guide

This guide helps you set up PostgreSQL locally for testing before using Docker.

## Quick Setup (macOS)

### Option 1: Using the Setup Script

```bash
./setup-local-postgres.sh
```

### Option 2: Manual Setup

#### 1. Install PostgreSQL

```bash
# Install PostgreSQL 15
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15
```

#### 2. Install pgvector Extension

```bash
# Install pgvector
brew install pgvector
```

#### 3. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres -d postgres

# Create database
CREATE DATABASE ecocash_assistant;

# Connect to the new database
\c ecocash_assistant

# Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

# Verify extension is installed
\dx

# Exit
\q
```

#### 4. Configure Backend

Create or update `backend/.env`:

```bash
POSTGRES_URI=postgresql://postgres@localhost:5432/ecocash_assistant
OPENAI_API_KEY=your_openai_api_key
```

**Note**: If PostgreSQL requires a password, use:
```bash
POSTGRES_URI=postgresql://postgres:your_password@localhost:5432/ecocash_assistant
```

## Verify Setup

### Test Database Connection

```bash
# Test connection
psql -U postgres -d ecocash_assistant -c "SELECT version();"

# Check pgvector extension
psql -U postgres -d ecocash_assistant -c "\dx"
```

You should see `vector` in the extension list.

### Test Backend Connection

1. Make sure backend is running
2. Check backend logs for connection messages
3. The backend will automatically use PostgreSQL if `POSTGRES_URI` is set

## Troubleshooting

### PostgreSQL Not Starting

```bash
# Check status
brew services list

# Restart PostgreSQL
brew services restart postgresql@15

# Check logs
tail -f /usr/local/var/log/postgresql@15.log
```

### Connection Refused

- Ensure PostgreSQL is running: `brew services list`
- Check if port 5432 is in use: `lsof -i :5432`
- Verify connection string in `.env`

### pgvector Extension Not Found

```bash
# Reinstall pgvector
brew reinstall pgvector

# Or install from source
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
make install
```

### Permission Denied

If you get permission errors:

```bash
# Create postgres user (if needed)
createuser -s postgres

# Or use your macOS username
psql -U $(whoami) -d postgres
```

## Testing Session Persistence

1. Start a conversation in the frontend
2. Send a few messages
3. Restart the backend server
4. Continue the conversation - it should remember previous messages
5. Check database:

```bash
psql -U postgres -d ecocash_assistant -c "SELECT COUNT(*) FROM checkpoints;"
```

## Switching to Docker Later

When ready to test with Docker:

1. Stop local PostgreSQL: `brew services stop postgresql@15`
2. Update `POSTGRES_URI` in `backend/.env` to:
   ```
   POSTGRES_URI=postgresql://postgres:password@localhost:5432/ecocash_assistant
   ```
3. Start Docker Compose: `docker-compose up -d postgres`
4. Restart backend to pick up new connection

## Connection Strings

### Local PostgreSQL (no password)
```
postgresql://postgres@localhost:5432/ecocash_assistant
```

### Local PostgreSQL (with password)
```
postgresql://postgres:your_password@localhost:5432/ecocash_assistant
```

### Docker PostgreSQL
```
postgresql://postgres:password@localhost:5432/ecocash_assistant
```

