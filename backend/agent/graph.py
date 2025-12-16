"""
Ecocash Agent Graph.
Defines the workflow for the Ecocash Assistant.
"""

from typing import cast, Optional
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient  # MongoDBSaver requires synchronous pymongo client
import os
from langchain_core.runnables import RunnableConfig
from copilotkit.langgraph import copilotkit_emit_message
import logging

# Import context variable for Sasai token
# We MUST use the same ContextVar instance from app.context, otherwise the token won't be accessible
from app.context import sasai_token_context

logger = logging.getLogger(__name__)

# Import Ecocash chat node
from engine.chat import chat_node
from engine.state import AgentState

# Import Ecocash tools
# Import MCP Client
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from langchain_mcp_adapters.tools import load_mcp_tools

# We will load tools dynamically from MCP server
# from agent.tools import get_balance, list_transactions, create_ticket, get_transaction_details, get_cash_flow_overview, get_incoming_insights, get_investment_insights, get_spends_insights

# Import workflow subgraphs
from agent.workflows.subgraphs import detect_workflow_intent, get_workflow_subgraph
from agent.workflows.subgraphs.transaction_help_graph import build_transaction_help_subgraph
from agent.workflows.subgraphs.refund_graph import build_refund_subgraph
from agent.workflows.subgraphs.loan_enquiry_graph import build_loan_enquiry_graph
from agent.workflows.subgraphs.card_issue_graph import build_card_issue_subgraph
from agent.workflows.subgraphs.general_enquiry_graph import build_general_enquiry_subgraph
from agent.workflows.subgraphs.financial_insights_graph import build_financial_insights_subgraph

# Node for ticket confirmation (human-in-the-loop)
async def ticket_confirmation_node(state: AgentState, config: RunnableConfig):
    """Shows confirmation dialog and waits for user response."""
    thread_id = config.get("configurable", {}).get("thread_id", "NO_THREAD_ID")
    print(f"[TICKET_CONFIRMATION] Node executed with thread_id: {thread_id}")
    return state

# Node to perform ticket creation after confirmation
async def perform_ticket_node(state: AgentState, config: RunnableConfig):
    """Execute ticket creation after user confirmation."""
    messages = state.get("messages", [])
    
    # Get the tool message (user's confirmation response)
    tool_message = None
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage):
            tool_message = msg
            break
    
    # Get the AI message with tool call
    ai_message = None
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.tool_calls:
            ai_message = msg
            break
    
    if tool_message and ai_message:
        # Check if user cancelled
        if tool_message.content == "CANCEL":
            logger.info("Ticket creation cancelled by user")
            cancel_msg = AIMessage(content="Ticket creation cancelled. Is there anything else I can help you with?")
            state["messages"].append(cancel_msg)
            await copilotkit_emit_message(config, cancel_msg.content)
            return state
        
        # User confirmed - proceed with ticket creation
        if tool_message.content == "CONFIRM" or tool_message.content.startswith("CONFIRM"):
            logger.info("Ticket creation confirmed, executing create_ticket tool")
            try:
                # Execute the actual ticket creation via MCP
                mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp")
                
                async with sse_client(mcp_url) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        
                        # Find the last AIMessage with tool_calls
                        original_tool_call = None
                        for msg in reversed(messages):
                            if isinstance(msg, AIMessage) and msg.tool_calls:
                                for tc in msg.tool_calls:
                                    if tc["name"] == "create_ticket":
                                        original_tool_call = tc
                                        break
                                if original_tool_call:
                                    break
                        
                        if original_tool_call:
                            result = await session.call_tool("create_ticket", arguments=original_tool_call["args"])
                            # Extract text content from result
                            ticket_result = ""
                            if result.content:
                                for item in result.content:
                                    if item.type == "text":
                                        ticket_result += item.text
                            if not ticket_result:
                                ticket_result = "Ticket created."
                            
                            # Create ToolMessage
                            tool_msg = ToolMessage(
                                tool_call_id=original_tool_call["id"],
                                name="create_ticket",
                                content=ticket_result
                            )
                            
                            # We need to return state update
                            result_state = state.copy()
                            result_state["messages"].append(tool_msg)
                        else:
                            raise Exception("Could not find original ticket creation request")
                
                # Get the ticket result
                tool_messages = [msg for msg in result_state.get("messages", []) if isinstance(msg, ToolMessage)]
                if tool_messages:
                    ticket_result = tool_messages[-1].content
                    
                    # Extract ticket ID from the result (format: "Support ticket TICKET-12345 created...")
                    import re
                    ticket_id_match = re.search(r'TICKET-\d+', ticket_result)
                    ticket_id = ticket_id_match.group(0) if ticket_id_match else "N/A"
                    
                    logger.info(f"Ticket created successfully: {ticket_id}")
                    
                    # Create a clear success message with prominent ticket ID
                    success_msg = AIMessage(
                        content=f"✅ Your support request has been successfully submitted!\n\n"
                               f"📋 Ticket ID: {ticket_id}\n\n"
                               f"Please save this ticket ID for your records. You can use it to track the status of your request. "
                               f"Our support team will review your request and get back to you shortly. "
                               f"Is there anything else I can help you with?"
                    )
                    result_state["messages"].append(success_msg)
                    await copilotkit_emit_message(config, success_msg.content)
                
                return result_state
            except Exception as e:
                logger.error(f"Failed to create ticket: {e}", exc_info=True)
                error_msg = AIMessage(content="I encountered an error while creating your ticket. Please try again or contact support directly.")
                state["messages"].append(error_msg)
                await copilotkit_emit_message(config, error_msg.content)
                return state
    
    return state

# Intent detection node
async def detect_intent_node(state: AgentState, config: RunnableConfig):
    """Detect workflow intent and send welcome message for new sessions.
    Only detects intent if no workflow is currently active.
    """
    thread_id = config.get("configurable", {}).get("thread_id", "NO_THREAD_ID")
    print(f"[DETECT_INTENT] Node executed with thread_id: {thread_id}")
    
    messages = state.get("messages", [])
    user_messages = [msg for msg in messages if isinstance(msg, HumanMessage)]
    
    # If this is a new session (no user messages), send welcome message first
    if len(user_messages) == 0:
        from copilotkit.langgraph import copilotkit_emit_message
        welcome_msg = "How can I help you today?"
        welcome_ai_msg = AIMessage(content=welcome_msg)
        state["messages"].append(welcome_ai_msg)
        await copilotkit_emit_message(config, welcome_msg)
        # Return state to end the flow (welcome message sent, wait for user input)
        return state
    
    # Only detect intent if no workflow is already active
    current_workflow = state.get("current_workflow")
    if current_workflow:
        logger.debug(f"Intent detection skipped: workflow '{current_workflow}' already active")
        return state
    if messages:
        # Get the last user message (HumanMessage)
        last_user_message = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                last_user_message = msg
                break
        
        if last_user_message:
            user_message = str(last_user_message.content) if hasattr(last_user_message, 'content') else ""
            if user_message:
                logger.debug(f"Detecting workflow intent from user message: {user_message[:100]}...")
                workflow_name = detect_workflow_intent(user_message)
                if workflow_name:
                    # 🎯 LOG 2: Intent Detected
                    logger.info(f"🟢 [2/4] INTENT DETECTED: '{workflow_name}'")
                    state["current_workflow"] = workflow_name
                    return state
                else:
                    # 🎯 LOG 2: No specific intent, general chat
                    logger.info(f"🟢 [2/4] INTENT DETECTED: 'general_chat' (no specific workflow)")
                    logger.debug("No workflow intent detected, routing to chat_node")
    return state

# ----------------------------------------------------------------------
# Build the graph
# ----------------------------------------------------------------------
graph_builder = StateGraph(AgentState)

# Add nodes
graph_builder.add_node("chat_node", chat_node)
graph_builder.add_node("detect_intent", detect_intent_node)


# Define a function to get tools from MCP server
async def get_remittance_tools():
    # Connect to MCP server via SSE
    # Note: In a real production app, you might want to manage the connection lifecycle better
    # For this implementation, we'll assume the server is running at the default URL
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp")
    
    async with sse_client(mcp_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Load tools from MCP server
            tools = await load_mcp_tools(session)
            return tools

# Since we can't easily make the ToolNode async at build time in this structure,
# we might need to wrap it or initialize it differently.
# However, for this refactor, we will assume the tools are available or use a placeholder
# and let the runtime handle it. 
# A better approach for LangGraph with async tools setup might be needed.
# For now, let's try to load them if we are in an async context, or define a node that loads them.

# Alternative: Define a node that executes tools using the MCP client directly
def extract_token_from_config(config: RunnableConfig) -> Optional[str]:
    """
    Extract Sasai authentication token from LangGraph config.
    
    CopilotKit may pass tokens through config metadata, tags, or configurable.
    This function checks multiple possible locations.
    
    Args:
        config: LangGraph RunnableConfig object
        
    Returns:
        Token string if found, None otherwise
    """
    # Check configurable metadata
    configurable = config.get("configurable", {})
    
    # Check for token in various possible locations
    # Priority: external_token > sasai_token > token > auth_token
    token = (
        configurable.get("external_token") or
        configurable.get("sasai_token") or
        configurable.get("sasaiToken") or
        configurable.get("token") or
        configurable.get("auth_token") or
        config.get("tags", {}).get("external_token") or
        config.get("tags", {}).get("sasai_token") or
        config.get("tags", {}).get("sasaiToken") or
        config.get("metadata", {}).get("external_token") or
        config.get("metadata", {}).get("sasai_token") or
        config.get("metadata", {}).get("sasaiToken")
    )
    
    # If token is in "Bearer <token>" format, extract just the token
    if token and isinstance(token, str) and token.startswith("Bearer "):
        token = token.replace("Bearer ", "").strip()
    
    if token:
        logger.debug(f"[TOKEN_EXTRACT] Found external token (preview): {token[:20]}...")
    else:
        logger.debug("[TOKEN_EXTRACT] No external token found in config")
    
    return token


async def execute_mcp_tools(state: AgentState, config: RunnableConfig):
    """Execute tools using remote MCP server."""
    logger.debug("[MCP_TOOL] execute_mcp_tools called")
    messages = state.get("messages", [])
    if not messages:
        logger.debug("[MCP_TOOL] No messages in state")
        return state
        
    last_msg = messages[-1]
    if not isinstance(last_msg, AIMessage) or not last_msg.tool_calls:
        logger.debug(f"[MCP_TOOL] Last message is not AIMessage with tool_calls. Type: {type(last_msg)}")
        return state
        
    logger.debug(f"[MCP_TOOL] Found {len(last_msg.tool_calls)} tool call(s)")
    
    # Extract external token from config if available
    logger.debug("[MCP_TOOL] Starting token extraction...")
    external_token = extract_token_from_config(config)
    logger.debug(f"[MCP_TOOL] Token from config: {'Found' if external_token else 'NOT FOUND'}")
    
    # Also try to get token from context variable (set by middleware)
    # This is a workaround for CopilotKit not forwarding custom headers/metadata
    if not external_token:
        try:
            token_from_context = sasai_token_context.get()
            if token_from_context:
                external_token = token_from_context
                logger.info(f"[MCP_TOOL] ✅ Found Sasai token in context (preview): {external_token[:20]}...")
            else:
                logger.debug("[MCP_TOOL] Token from context: NOT FOUND")
        except LookupError as e:
            logger.warning(f"[MCP_TOOL] ContextVar not set in this context: {e}")
        except Exception as e:
            logger.warning(f"[MCP_TOOL] Could not access token from context: {type(e).__name__}: {e}", exc_info=True)
    
    use_token_manager = os.getenv("USE_TOKEN_MANAGER", "true").lower() == "true"
    logger.debug(f"[MCP_TOOL] Token manager enabled: {use_token_manager}, External token available: {bool(external_token)}")
    
    # If token manager is disabled, we must have an external token
    if not use_token_manager and not external_token:
        logger.warning("[MCP_TOOL] Token manager is disabled but no external token found in config")
    
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp")
    results = []
    
    async with sse_client(mcp_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            for tool_call in last_msg.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"].copy() if tool_call["args"] else {}
                
                logger.debug(f"[MCP_TOOL] Processing tool: {tool_name}")
                
                # ALWAYS inject external_token if provided (takes precedence over token manager)
                # If token manager is disabled, external_token is required
                if external_token:
                    tool_args["external_token"] = external_token
                    logger.info(f"[MCP_TOOL] ✅ Injected external_token for {tool_name} (preview: {external_token[:20]}...)")
                elif not use_token_manager:
                    logger.error(f"[MCP_TOOL] ❌ Token manager disabled but no external_token provided for {tool_name}")
                    # Don't inject None - let the tool handle the error
                else:
                    logger.debug(f"[MCP_TOOL] No external token, will use token manager for {tool_name}")
                
                try:
                    # Call the tool on the MCP server
                    # 🎯 LOG 4: Tool Call
                    logger.info(f"🟠 [4/4] TOOL CALL: {tool_name}({', '.join([f'{k}={v}' for k, v in tool_args.items() if k != 'external_token'])})")
                    
                    result = await session.call_tool(tool_name, arguments=tool_args)
                    
                    # Log the raw MCP result structure
                    logger.info(f"[MCP_TOOL] Tool: {tool_name}")
                    logger.info(f"[MCP_TOOL] Result type: {type(result)}")
                    logger.info(f"[MCP_TOOL] Result content items: {len(result.content) if hasattr(result, 'content') else 0}")
                    
                    # Format result for LangChain
                    content = ""
                    for content_item in result.content:
                        if content_item.type == "text":
                            content += content_item.text
                            # Log the content for transaction tools
                            if tool_name == "get_wallet_transaction_history":
                                logger.info(f"[MCP_TOOL] Content preview (first 500 chars): {content[:500]}")
                        # Handle other content types if needed
                    
                    # Log final content for transaction tools
                    if tool_name == "get_wallet_transaction_history":
                        logger.info(f"[MCP_TOOL] Final content length: {len(content)}")
                        try:
                            import json
                            parsed_content = json.loads(content)
                            logger.info(f"[MCP_TOOL] Parsed content keys: {list(parsed_content.keys()) if isinstance(parsed_content, dict) else 'Not a dict'}")
                            if isinstance(parsed_content, dict) and 'data' in parsed_content:
                                data = parsed_content['data']
                                logger.info(f"[MCP_TOOL] Data type: {type(data)}")
                                if isinstance(data, dict):
                                    logger.info(f"[MCP_TOOL] Data keys: {list(data.keys())}")
                                elif isinstance(data, list):
                                    logger.info(f"[MCP_TOOL] Data is list with {len(data)} items")
                        except Exception as e:
                            logger.warning(f"[MCP_TOOL] Could not parse content as JSON: {e}")
                    
                    results.append(ToolMessage(
                        tool_call_id=tool_call["id"],
                        name=tool_name,
                        content=content
                    ))
                except Exception as e:
                    logger.error(f"Error calling MCP tool {tool_name}: {e}")
                    results.append(ToolMessage(
                        tool_call_id=tool_call["id"],
                        name=tool_name,
                        content=f"Error: {str(e)}"
                    ))
    
    return {"messages": results}

# Replace the static ToolNode with our dynamic MCP executor
graph_builder.add_node("remittance_tools", execute_mcp_tools)
graph_builder.add_node("ticket_confirmation", ticket_confirmation_node)
graph_builder.add_node("perform_ticket", perform_ticket_node)

# Add workflow subgraphs as nodes
# Compile subgraphs at graph build time (not import time)
graph_builder.add_node("transaction_help", build_transaction_help_subgraph())
graph_builder.add_node("financial_insights", build_financial_insights_subgraph())
graph_builder.add_node("refund", build_refund_subgraph())
graph_builder.add_node("loan_enquiry", build_loan_enquiry_graph())
graph_builder.add_node("card_issue", build_card_issue_subgraph())
graph_builder.add_node("general_enquiry", build_general_enquiry_subgraph())

# Define routing logic after chat node
def route_after_chat(state: AgentState):
    messages = state.get("messages", [])
    if messages and isinstance(messages[-1], AIMessage):
        ai_msg = cast(AIMessage, messages[-1])
        if ai_msg.tool_calls:
            tool_name = ai_msg.tool_calls[0]["name"]
            # Route to ticket confirmation for create_ticket
            if tool_name == "create_ticket":
                return "ticket_confirmation"
            # Route to tools for other tools
            return "remittance_tools"
    
    # Don't route back to subgraphs from chat_node
    # Subgraphs are only for initial summarization
    # After subgraph completes, conversation continues normally in chat_node
    return END

# Define routing logic after intent detection
def route_after_intent(state: AgentState):
    """Route to appropriate workflow subgraph or continue to chat."""
    current_workflow = state.get("current_workflow")
    workflow_step = state.get("workflow_step")
    
    # Only route to subgraph if workflow is detected and not yet completed
    if current_workflow and workflow_step != "completed":
        return current_workflow
    
    # Otherwise, go to chat_node
    return "chat_node"

# Define routing logic after ticket confirmation
def route_after_confirmation(state: AgentState):
    messages = state.get("messages", [])
    # After interrupt, user response comes as a ToolMessage
    if messages and isinstance(messages[-1], ToolMessage):
        tool_msg = cast(ToolMessage, messages[-1])
        # Check if this is a confirmation response
        if tool_msg.content in ["CONFIRM", "CANCEL"] or tool_msg.content.startswith("CONFIRM"):
            return "perform_ticket"
    return END

# Add edges
# Always start with intent detection
graph_builder.add_edge(START, "detect_intent")
graph_builder.add_conditional_edges(
    "detect_intent",
    route_after_intent,
    {
        "transaction_help": "transaction_help",
        "financial_insights": "financial_insights",
        "refund": "refund",
        "loan_enquiry": "loan_enquiry",
        "card_issue": "card_issue",
        "general_enquiry": "general_enquiry",
        "chat_node": "chat_node"  # No workflow detected or already processed
    }
)
# After workflow subgraphs, continue to chat
# Subgraphs complete their summarization and pass control to chat_node
# chat_node will handle the rest of the conversation
graph_builder.add_edge("transaction_help", "chat_node")
graph_builder.add_edge("financial_insights", "chat_node")
graph_builder.add_edge("refund", "chat_node")
graph_builder.add_edge("loan_enquiry", "chat_node")
graph_builder.add_edge("card_issue", "chat_node")
graph_builder.add_edge("general_enquiry", "chat_node")
graph_builder.add_conditional_edges(
    "chat_node",
    route_after_chat,
    {
        "remittance_tools": "remittance_tools",
        "ticket_confirmation": "ticket_confirmation",
        END: END
    }
)
graph_builder.add_edge("remittance_tools", "chat_node")
graph_builder.add_conditional_edges(
    "ticket_confirmation",
    route_after_confirmation,
    {"perform_ticket": "perform_ticket", END: END}
)
graph_builder.add_edge("perform_ticket", "chat_node")

# Initialize MongoDB checkpointer
# According to MongoDB docs: https://www.mongodb.com/docs/atlas/ai-integrations/langgraph/
# MongoDBSaver requires pymongo.MongoClient (synchronous), not AsyncIOMotorClient
# MongoDBSaver handles async operations internally via its async methods
_checkpointer = None
_mongo_client = None  # Keep MongoDB client alive

async def get_checkpointer():
    """Get MongoDB checkpointer from environment variable.
    
    Returns MongoDBSaver for async execution (required by CopilotKit).
    This must be called from an async context (e.g., FastAPI startup event).
    
    According to MongoDB docs: https://www.mongodb.com/docs/atlas/ai-integrations/langgraph/
    MongoDBSaver requires pymongo.MongoClient (synchronous), but it provides
    async methods (aput, aget, etc.) that work with LangGraph's async execution.
    """
    global _checkpointer, _mongo_client
    
    if _checkpointer is not None:
        return _checkpointer
    
    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_db_name = os.getenv("MONGODB_DB_NAME", "remittance_assistant")
    
    if mongodb_uri:
        try:
            # According to MongoDB LangGraph docs, MongoDBSaver requires pymongo.MongoClient
            # (synchronous client), not AsyncIOMotorClient
            # MongoDBSaver provides async methods internally for LangGraph
            _mongo_client = MongoClient(mongodb_uri)
            
            # Test connection
            _mongo_client.admin.command('ping')
            
            # Create MongoDB checkpointer with synchronous pymongo client
            # MongoDBSaver will handle async operations via its async methods
            # Collections are created automatically on first use
            _checkpointer = MongoDBSaver(_mongo_client, db_name=mongodb_db_name)
            
            logger.info(f"✅ Using MongoDBSaver for session persistence (database: {mongodb_db_name})")
            return _checkpointer
        except Exception as e:
            logger.warning(f"Failed to initialize MongoDBSaver: {e}. Falling back to MemorySaver.")
            logger.exception(e)
            from langgraph.checkpoint.memory import MemorySaver
            _checkpointer = MemorySaver()
            return _checkpointer
    else:
        logger.warning("MONGODB_URI not set. Using MemorySaver (sessions will not persist).")
        from langgraph.checkpoint.memory import MemorySaver
        _checkpointer = MemorySaver()
        return _checkpointer

def get_checkpointer_sync():
    """Get appropriate checkpointer based on environment (synchronous).
    
    This function is designed for SDK initialization at module load time.
    It respects the USE_IN_MEMORY_DB flag to support both local dev (MemorySaver)
    and production (MongoDB) without requiring runtime updates.
    
    Returns:
        BaseCheckpointSaver: Either MemorySaver (in-memory) or MongoDBSaver (persistent)
    """
    # Check if we should use in-memory database (for local dev/testing)
    use_memory = os.getenv("USE_IN_MEMORY_DB", "false").lower() == "true"
    
    if use_memory:
        logger.info("🧪 Using MemorySaver checkpointer (in-memory, non-persistent)")
        from langgraph.checkpoint.memory import MemorySaver
        return MemorySaver()
    
    # Production mode: Use MongoDB checkpointer
    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_db_name = os.getenv("MONGODB_DB_NAME", "remittance-assistance-agent")
    
    if not mongodb_uri:
        logger.warning("⚠️  MONGODB_URI not set, falling back to MemorySaver")
        logger.warning("    Set USE_IN_MEMORY_DB=true for intentional in-memory mode")
        from langgraph.checkpoint.memory import MemorySaver
        return MemorySaver()
    
    try:
        # Create sync MongoDB client for initialization
        # MongoDBSaver requires pymongo.MongoClient (synchronous), not motor
        # It provides async methods internally for LangGraph
        client = MongoClient(mongodb_uri)
        
        # Test connection
        client.admin.command('ping')
        logger.info(f"✅ MongoDB connection successful")
        
        # Create checkpointer
        checkpointer = MongoDBSaver(client, db_name=mongodb_db_name)
        logger.info(f"✅ Using MongoDBSaver for persistent sessions (db: {mongodb_db_name})")
        
        return checkpointer
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize MongoDB checkpointer: {e}")
        logger.warning("⚠️  Falling back to MemorySaver (sessions will not persist)")
        from langgraph.checkpoint.memory import MemorySaver
        return MemorySaver()

# Compile graph with interrupt for human-in-the-loop
def build_graph(checkpointer=None):
    """Build and compile the graph with checkpointer.
    
    Args:
        checkpointer: Optional checkpointer. If None, uses get_checkpointer_sync()
                     which returns the appropriate checkpointer based on environment
                     (MemorySaver for local dev, MongoDBSaver for production).
    """
    if checkpointer is None:
        checkpointer = get_checkpointer_sync()
    
    compiled = graph_builder.compile(
        interrupt_after=["ticket_confirmation"],
        checkpointer=checkpointer,
    )
    checkpointer_type = type(checkpointer).__name__
    logger.info(f"📊 Graph compiled with {checkpointer_type} checkpointer")
    return compiled
