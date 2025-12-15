import asyncio
import os
import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client

async def check_endpoint(url):
    print(f"Checking {url}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers={"Accept": "text/event-stream"})
            print(f"Status: {response.status_code}")
            print(f"Headers: {response.headers}")
            print(f"Content: {response.text[:200]}")
            return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

async def verify_mcp():
    base_url = "http://localhost:8000"
    endpoints = [
        "/mcp",
        "/mcp/",
        "/mcp/sse",
        "/sse",
        "/events"
    ]
    
    valid_url = None
    for ep in endpoints:
        url = f"{base_url}{ep}"
        if await check_endpoint(url):
            valid_url = url
            break
            
    if not valid_url:
        # If no 200 OK, maybe one of them is the correct one but needs specific handling
        # The 400 "Missing session ID" on /mcp is the most promising lead.
        # It implies it IS the endpoint but expects something.
        print("\n⚠️ Could not find a simple 200 OK endpoint. Retrying /mcp with sse_client...")
        valid_url = f"{base_url}/mcp"

    print(f"\nConnecting to MCP server at {valid_url}...")
    
    try:
        async with sse_client(valid_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # List tools
                print("\nListing tools...")
                tools = await session.list_tools()
                print(f"Found {len(tools.tools)} tools:")
                for tool in tools.tools:
                    print(f"- {tool.name}: {tool.description[:50]}...")
                
                # Test a tool call
                print("\nTesting get_incoming_insights...")
                result = await session.call_tool("get_incoming_insights", arguments={"user_id": "test_user"})
                print("Result:", result)
                
                print("\n✅ Verification complete!")
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n❌ Verification failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_mcp())
