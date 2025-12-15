from dotenv import load_dotenv
load_dotenv()

import os
from typing import Optional, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitRemoteEndpoint, LangGraphAgent
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import json

from agent.graph import build_graph
from app.sessions import router as sessions_router
from app.auth import extract_sasai_token_from_request
from app.context import sasai_token_context, language_context

# Configure logging - reduce verbosity of CopilotKit SDK logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Silence noisy CopilotKit SDK logs (they log Thread ID, Node Name, State, Config, Messages at INFO level)
logging.getLogger("copilotkit.sdk").setLevel(logging.WARNING)
logging.getLogger("copilotkit").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Read ROOT_PATH from environment variable for reverse proxy support
# This is needed when the ingress doesn't strip the path prefix
# Set ROOT_PATH="/ecocash-backend" if path rewrite isn't working
ROOT_PATH = os.getenv("ROOT_PATH", "")

app = FastAPI(
    title="Ecocash Assistant Backend",
    root_path=ROOT_PATH  # Add root_path for reverse proxy support
)

# Configure CORS origins from environment variable
# CORS_ORIGINS can be a comma-separated list of origins
def normalize_origin(origin: str) -> str:
    """Normalize CORS origin by removing path components.
    
    CORS origins should be protocol + domain + port only, not include paths.
    This function strips any path components if accidentally included.
    """
    origin = origin.strip()
    # Remove path if present (everything after the third slash)
    # e.g., "https://example.com/path" -> "https://example.com"
    if "://" in origin:
        parts = origin.split("://", 1)
        if len(parts) == 2:
            protocol = parts[0]
            rest = parts[1]
            # Remove path (everything after first slash)
            domain_port = rest.split("/")[0]
            return f"{protocol}://{domain_port}"
    return origin

def get_cors_origins() -> List[str]:
    """Get CORS allowed origins from environment variable or use defaults."""
    # Default localhost origins for local development
    default_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
    
    # Read from environment variable (set in Kubernetes configmap)
    cors_origins_env = os.getenv("CORS_ORIGINS")
    
    if cors_origins_env:
        # Split by comma and strip whitespace, then normalize each origin
        origins = [
            normalize_origin(origin) 
            for origin in cors_origins_env.split(",") 
            if origin.strip()
        ]
        # Combine with default localhost origins for development
        all_origins = default_origins + origins
        # Remove duplicates while preserving order
        seen = set()
        unique_origins = []
        for origin in all_origins:
            if origin not in seen:
                seen.add(origin)
                unique_origins.append(origin)
        logger.info(f"CORS origins configured: {unique_origins}")
        return unique_origins
    else:
        # Fallback to localhost only if no environment variable is set
        logger.warning("CORS_ORIGINS environment variable not set, using localhost only")
        return default_origins

# Add CORS middleware to allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Middleware to extract Sasai token from request and store it in context for LangGraph
class SasaiTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        sasai_token = None
        body_data = None
        
        # First try to extract from HTTP headers
        logger.debug(f"[MIDDLEWARE] Checking for Sasai token in request to: {request.url.path}")
        sasai_token = extract_sasai_token_from_request(request)
        
        # If not in headers, try to extract from request body (CopilotKit properties)
        # CopilotKit sends properties in the request body, not as HTTP headers
        if not sasai_token and request.method == "POST" and "/api/copilotkit" in request.url.path:
            try:
                # Read the body
                body_bytes = await request.body()
                if body_bytes:
                    body_data = json.loads(body_bytes)
                    
                    # 🎯 LOG 1: Query from Frontend
                    messages = body_data.get("messages", [])
                    if messages:
                        last_message = messages[-1]
                        if isinstance(last_message, dict) and last_message.get("role") == "user":
                            user_query = last_message.get("content", "")
                            logger.info(f"🔵 [1/4] QUERY FROM FRONTEND: {user_query}")
                    
                    properties = body_data.get("properties", {})
                    
                    # Check headers in properties (CopilotKit forwards these)
                    props_headers = properties.get("headers", {})
                    sasai_token = props_headers.get("X-Sasai-Token") or props_headers.get("x-sasai-token")
                    
                    # Also check metadata
                    if not sasai_token:
                        metadata = properties.get("metadata", {})
                        sasai_token = metadata.get("external_token") or metadata.get("sasai_token") or metadata.get("sasaiToken")
                    
                    if sasai_token:
                        logger.info(f"[MIDDLEWARE] ✅ Found Sasai token in request body properties (preview): {sasai_token[:20]}...")
                    
                    # Recreate request body stream for downstream handlers
                    async def receive():
                        return {"type": "http.request", "body": body_bytes}
                    request._receive = receive
            except json.JSONDecodeError as e:
                logger.debug(f"[MIDDLEWARE] Could not parse request body as JSON: {e}")
            except Exception as e:
                logger.debug(f"[MIDDLEWARE] Error reading request body: {type(e).__name__}: {e}", exc_info=True)
        
        # Store token in context variable for LangGraph nodes to access
        if sasai_token:
            sasai_token_context.set(sasai_token)
            logger.info(f"[MIDDLEWARE] ✅ Stored Sasai token in context variable")
        else:
            logger.debug("[MIDDLEWARE] No Sasai token found - token manager will be used")
            sasai_token_context.set(None)
        
        # Extract language preference from headers or metadata
        language = "en"  # Default to English
        
        # Check X-Language header first
        language_header = request.headers.get("X-Language") or request.headers.get("x-language")
        if language_header and language_header in ["en", "sn"]:
            language = language_header
        elif body_data:
            # Extract from request body metadata
            try:
                properties = body_data.get("properties", {})
                metadata = properties.get("metadata", {})
                lang_from_metadata = metadata.get("language")
                if lang_from_metadata and lang_from_metadata in ["en", "sn"]:
                    language = lang_from_metadata
            except Exception as e:
                logger.debug(f"[MIDDLEWARE] Could not extract language from body: {e}")
        
        # Store language in context variable
        language_context.set(language)
        logger.debug(f"[MIDDLEWARE] Language preference: {language}")
        
        response = await call_next(request)
        return response

app.add_middleware(SasaiTokenMiddleware)

# Include sessions router
app.include_router(sessions_router)

# Initialize graph with proper checkpointer at module load
# Uses environment-based configuration (USE_IN_MEMORY_DB flag)
# No runtime updates needed - restart required to change checkpointer type
graph = build_graph()  # Calls get_checkpointer_sync() internally
sdk = CopilotKitRemoteEndpoint(
    agents=[
        LangGraphAgent(
            name="ecocash_agent",
            description="Ecocash Relationship Manager",
            graph=graph,
        )
    ],
)

# Register endpoint with properly initialized SDK
add_fastapi_endpoint(app, sdk, "/api/copilotkit")
logger.info("✅ CopilotKit endpoint registered at /api/copilotkit")

@app.get("/")
async def root():
    return {"message": "Ecocash Assistant Backend is running"}
