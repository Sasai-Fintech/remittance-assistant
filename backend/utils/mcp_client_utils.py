
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from langchain_mcp_adapters.tools import load_mcp_tools
import logging

logger = logging.getLogger(__name__)

async def get_mcp_tools():
    """
    Connect to the MCP server and load available tools.
    Returns a list of LangChain compatible tools.
    """
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp")
    
    try:
        logger.info(f"Attempting to connect to MCP server at: {mcp_url}")
        async with sse_client(mcp_url) as (read, write):
            logger.info("SSE client connection established")
            async with ClientSession(read, write) as session:
                logger.info("Initializing MCP session...")
                await session.initialize()
                logger.info("Loading MCP tools...")
                # Load tools from MCP server
                # This returns a list of LangChain tools that are bound to this session
                # Note: These tools will fail if executed after session closes,
                # but we only need them for binding to the LLM (getting schemas).
                tools = await load_mcp_tools(session)
                logger.info(f"Successfully loaded {len(tools)} MCP tools")
                return tools
    except Exception as e:
        logger.error(f"Failed to load MCP tools: {e}", exc_info=True)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []
