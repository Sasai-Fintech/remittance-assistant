#!/usr/bin/env python3
"""
Unified MCP Server Entry Point with Configurable Transport.

Supports three transport modes:
- stdio: Standard input/output (for Claude Desktop, local development)
- http: HTTP with SSE transport (for web clients)
- streamable_http: Streamable HTTP transport (for production)

Configure via MCP_TRANSPORT environment variable:
- MCP_TRANSPORT=stdio (default)
- MCP_TRANSPORT=http
- MCP_TRANSPORT=streamable_http
"""

import sys
import os
import asyncio
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
project_root = Path(__file__).parent
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded environment variables from {env_path}")
else:
    print(f"⚠️  No .env file found at {env_path}, using system environment variables")

# Ensure we can import from our src directory
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import from our modular structure
from core.server import initialize_server
from config.settings import SasaiConfig
from utils.helpers import setup_logging


def run_stdio_transport(server):
    """Run server with STDIO transport (synchronous)."""
    print("🔧 Transport: STDIO (Standard Input/Output)")
    print("💡 Use this for Claude Desktop integration or local development")
    print("---")
    # STDIO transport runs synchronously (blocking)
    server.run()


async def run_http_transport(server):
    """Run server with HTTP transport (SSE)."""
    host = os.getenv("MCP_HTTP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_HTTP_PORT", "8001"))
    path = os.getenv("MCP_HTTP_PATH", "/mcp")
    transport_type = os.getenv("MCP_HTTP_TRANSPORT", "sse")  # sse or websocket
    
    # print(f"🔧 Transport: HTTP ({transport_type.upper()})")
    # print(f"📡 Server URL: http://{host}:{port}{path}")
    # print(f"🔧 Host: {host}")
    # print(f"🔧 Port: {port}")
    # print(f"🔧 Path: {path}")
    # print("---")
    # print("💡 Client Connection:")
    # print(f"   URL: http://{host}:{port}{path}")
    # print(f"   Transport: SSE (Server-Sent Events)")
    # print("---")
    
    await server.run_http_async(
        transport=transport_type,
        host=host,
        port=port,
        path=path,
        log_level=SasaiConfig.LOG_LEVEL
    )


async def run_streamable_http_transport(server):
    """Run server with Streamable HTTP transport."""
    host = os.getenv("MCP_HTTP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_HTTP_PORT", "8001"))
    path = os.getenv("MCP_HTTP_PATH", "/mcp")
    
    print(f"🔧 Transport: Streamable HTTP")
    print(f"📡 Server URL: http://{host}:{port}{path}")
    print(f"🔧 Host: {host}")
    print(f"🔧 Port: {port}")
    print(f"🔧 Path: {path}")
    print("---")
    print("💡 Client Connection:")
    print(f"   URL: http://{host}:{port}{path}")
    print(f"   Transport: StreamableHttpTransport")
    print("---")
    
    # Check if streamable_http method exists
    if hasattr(server, 'run_streamable_http_async'):
        await server.run_streamable_http_async(
            host=host,
            port=port,
            path=path,
            log_level=SasaiConfig.LOG_LEVEL
        )
    else:
        # Fallback to regular HTTP with SSE
        print("⚠️  Streamable HTTP not available, falling back to HTTP with SSE")
        await run_http_transport(server)


async def main():
    """Main entry point with configurable transport."""
    try:
        # Set up logging
        logger = setup_logging(level=SasaiConfig.LOG_LEVEL)
        
        # Initialize the server with all tools
        print("🔧 Initializing MCP server...")
        server = initialize_server()
        print("✅ MCP server initialized successfully")
        print("---")
        
        # Get transport mode from environment
        transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
        
        # Validate transport mode
        valid_transports = ["stdio", "http", "streamable_http"]
        if transport not in valid_transports:
            print(f"❌ Invalid MCP_TRANSPORT: {transport}")
            print(f"   Valid options: {', '.join(valid_transports)}")
            sys.exit(1)
        
        # print(f"🚀 Starting Sasai Wallet MCP Server")
        # print(f"📦 Transport Mode: {transport.upper()}")
        print("---")
        
        # Run server with selected transport
        if transport == "stdio":
            # STDIO runs synchronously (blocking), so we run it directly
            run_stdio_transport(server)
        elif transport == "http":
            await run_http_transport(server)
        elif transport == "streamable_http":
            await run_streamable_http_transport(server)
            
    except KeyboardInterrupt:
        print("\n\n👋 Server shutdown requested by user")
        print("Goodbye!")
    except Exception as e:
        print(f"\n❌ Server startup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main_sync():
    """Synchronous wrapper for the async main function."""
    try:
        transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
        
        if transport == "stdio":
            # For STDIO, we can run synchronously
            import sys
            from pathlib import Path
            from dotenv import load_dotenv
            
            project_root = Path(__file__).parent
            env_path = project_root / ".env"
            if env_path.exists():
                load_dotenv(env_path)
            
            src_path = project_root / "src"
            sys.path.insert(0, str(src_path))
            
            from core.server import initialize_server
            from config.settings import SasaiConfig
            from utils.helpers import setup_logging
            
            logger = setup_logging(level=SasaiConfig.LOG_LEVEL)
            server = initialize_server()
            
            print("🚀 Starting Sasai Wallet MCP Server")
            print("📦 Transport Mode: STDIO")
            print("---")
            server.run()
        else:
            # For HTTP transports, use async
            asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Server shutdown requested by user")
        print("Goodbye!")
    except Exception as e:
        print(f"\n❌ Server startup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main_sync()

