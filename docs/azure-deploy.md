# Azure Container Apps Deployment Guide

This guide explains how to deploy the Remittance Assistant to Azure Container Apps.

## Prerequisites

- Azure CLI installed and configured
- Azure Container Registry (ACR) created
- Azure Container Apps environment created
- MongoDB Atlas cluster (or use existing MongoDB instance)

## Step 1: Build and Push Images to Azure Container Registry

```bash
# Login to Azure
az login

# Set variables
RESOURCE_GROUP="remittance-rg"
ACR_NAME="remittanceregistry"
LOCATION="eastus"

# Build and push backend image
az acr build --registry $ACR_NAME --image remittance-backend:latest ./backend

# Build and push frontend image
az acr build --registry $ACR_NAME --image remittance-frontend:latest ./frontend
```

## Step 2: Configure MongoDB

### Option A: MongoDB Atlas (Recommended)

1. **Create MongoDB Atlas Cluster** (if not already created):
   - Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Create a new cluster or use existing cluster
   - Create database user with read/write permissions
   - Whitelist Azure Container Apps IP ranges (or use 0.0.0.0/0 for development)

2. **Get Connection String**:
   - In MongoDB Atlas, go to "Connect" → "Connect your application"
   - Copy the connection string
   - Format: `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority`

### Option B: Azure Container Instance (Development - Local MongoDB)

```bash
az container create \
  --resource-group $RESOURCE_GROUP \
  --name remittance-mongodb \
  --image mongo:latest \
  --dns-name-label remittance-mongodb \
  --ports 27017 \
  --environment-variables \
    MONGO_INITDB_DATABASE=remittance_assistant
```

**Note**: For production, use MongoDB Atlas. The project already has MongoDB Atlas configured.

## Step 3: Create Container Apps Environment

```bash
# Create Container Apps environment
az containerapp env create \
  --name remittance-env \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

## Step 4: Deploy Backend Container App

```bash
# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)

# Create backend container app
az containerapp create \
  --name remittance-backend \
  --resource-group $RESOURCE_GROUP \
  --environment remittance-env \
  --image $ACR_LOGIN_SERVER/remittance-backend:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars \
    MONGODB_URI="@Microsoft.KeyVault(SecretUri=<your-mongodb-uri-secret-uri>)" \
    MONGODB_DB_NAME="remittance_assistant" \
    OPENAI_API_KEY="@Microsoft.KeyVault(SecretUri=<your-key-vault-secret-uri>)" \
  --registry-server $ACR_LOGIN_SERVER \
  --cpu 1.0 \
  --memory 2.0Gi \
  --min-replicas 1 \
  --max-replicas 3
```

## Step 5: Deploy Frontend Container App

```bash
# Get backend URL
BACKEND_URL=$(az containerapp show --name remittance-backend --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)

# Create frontend container app
az containerapp create \
  --name remittance-frontend \
  --resource-group $RESOURCE_GROUP \
  --environment remittance-env \
  --image $ACR_LOGIN_SERVER/remittance-frontend:latest \
  --target-port 3000 \
  --ingress external \
  --env-vars \
    NEXT_PUBLIC_REMOTE_ACTION_URL="https://$BACKEND_URL/api/copilotkit" \
  --registry-server $ACR_LOGIN_SERVER \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 1 \
  --max-replicas 2
```

## Step 6: Configure Health Probes

Health probes are automatically configured via Dockerfile HEALTHCHECK, but you can also configure them in Azure:

```bash
# Backend health probe
az containerapp update \
  --name remittance-backend \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars HEALTH_CHECK_PATH=/

# Frontend health probe
az containerapp update \
  --name remittance-frontend \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars HEALTH_CHECK_PATH=/api/health
```

## Step 7: Configure Networking

Ensure backend and frontend can communicate:

**For MongoDB Atlas:**
- Configure IP whitelist in MongoDB Atlas dashboard
- Add Azure Container Apps outbound IP addresses
- Or use 0.0.0.0/0 for development (not recommended for production)

## Environment Variables

### Backend
- `MONGODB_URI`: MongoDB connection string (store in Key Vault)
- `MONGODB_DB_NAME`: Database name for sessions (default: `remittance_assistant`)
- `OPENAI_API_KEY`: OpenAI API key (store in Key Vault)
- `REMOTE_ACTION_URL`: Backend URL (optional, for internal routing)

### Frontend
- `NEXT_PUBLIC_REMOTE_ACTION_URL`: Backend API URL
- `OPENAI_API_KEY`: (if needed for client-side operations)

## Scaling Configuration

### Backend
- Min replicas: 1
- Max replicas: 3
- CPU: 1.0
- Memory: 2.0Gi

### Frontend
- Min replicas: 1
- Max replicas: 2
- CPU: 0.5
- Memory: 1.0Gi

## Monitoring

View logs:
```bash
az containerapp logs show --name remittance-backend --resource-group $RESOURCE_GROUP --follow
az containerapp logs show --name remittance-frontend --resource-group $RESOURCE_GROUP --follow
```

## Troubleshooting

1. **Container won't start**: Check logs and ensure environment variables are set correctly
2. **Database connection fails**: Verify MongoDB Atlas IP whitelist and connection string
3. **Health checks failing**: Ensure health endpoints are accessible
4. **Images not found**: Verify ACR images are built and accessible

## Cost Optimization

- Use MongoDB Atlas free tier (M0) for development
- Set min-replicas to 0 for non-production environments
- Use Azure Container Apps consumption plan for pay-per-use pricing
- MongoDB Atlas offers free tier with 512MB storage

