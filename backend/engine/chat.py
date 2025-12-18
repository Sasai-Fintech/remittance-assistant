import json
import os
import logging
from engine.state import AgentState
from langchain_core.messages import SystemMessage
from langchain_openai import AzureChatOpenAI
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from typing import cast
from utils.mcp_client_utils import get_mcp_tools
from app.context import language_context

logger = logging.getLogger(__name__)

# Lazy initialization to avoid import-time errors
_llm = None

def get_llm():
    """Get or create the Azure OpenAI LLM instance."""
    global _llm
    if _llm is None:
        # Azure OpenAI configuration from environment variables
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://azureopenai-uswest-sandbox.openai.azure.com/")
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        
        if not azure_api_key:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
        
        # Using Azure OpenAI gpt-4o-mini deployment
        _llm = AzureChatOpenAI(
            azure_endpoint=azure_endpoint,
            azure_deployment=azure_deployment,
            api_key=azure_api_key,
            api_version=azure_api_version,
            temperature=0.7,
            max_tokens=4096,
        )
    return _llm

async def chat_node(state: AgentState, config: RunnableConfig):
    """Handle chat operations for Ecocash Assistant"""
    
    # Debug: Log thread_id from config
    thread_id = config.get("configurable", {}).get("thread_id", "NO_THREAD_ID")
    print(f"[CHAT_NODE] Executing with thread_id: {thread_id}")
    # print(f"[CHAT_NODE] Full configurable: {config.get('configurable', {})}")
    print(f"[CHAT_NODE] Config has checkpointer: {config.get('configurable', {}).get('thread_id') is not None}")
    # print(f"[CHAT_NODE] Full config: {config}")
    # print(f"[CHAT_NODE] Configurable keys: {list(config.get('configurable', {}).keys())}")
    
    # Detect user's language preference
    language = "en"  # Default to English
    
    # First, try to get from context variable (set by middleware)
    try:
        language = language_context.get()
    except LookupError:
        pass  # Context not set, continue with other methods
    
    # Also check config and metadata (from frontend)
    configurable = config.get("configurable", {})
    metadata = config.get("metadata", {})
    
    # Override with explicit language from config if present
    if "language" in configurable:
        language = configurable["language"]
    elif "language" in metadata:
        language = metadata["language"]
    
    # Also check the last user message for Shona indicators
    messages = state.get("messages", [])
    if messages:
        last_user_message = None
        for msg in reversed(messages):
            if hasattr(msg, "content") and hasattr(msg, "type"):
                if msg.type == "human":
                    last_user_message = msg.content
                    break
        
        if last_user_message:
            # Check for Shona words/phrases
            shona_indicators = [
                "mhoro", "ndinoda", "rubatsiro", "mari", "zvishandiswa",
                "muhomwe", "chishandiso", "mutengesi", "zvichangobva",
                "ndiri", "ndine", "pane", "zvakaitika", "zvakadaro"
            ]
            message_lower = last_user_message.lower()
            shona_count = sum(1 for word in shona_indicators if word in message_lower)
            
            # If significant Shona words detected, prefer Shona
            if shona_count >= 2:
                language = "sn"
    
    print(f"[CHAT_NODE] Detected language: {language}")
    
    # Get LLM instance (lazy initialization)
    llm = get_llm()
    
    # Get MCP tools dynamically
    tools = await get_mcp_tools()
    
    if not tools:
        print("[CHAT_NODE] WARNING: No tools loaded from MCP server!")
    else:
        print(f"[CHAT_NODE] Loaded {len(tools)} tools from MCP server")

    # Bind the Ecocash tools to the LLM
    llm_with_tools = llm.bind_tools(
        tools,
        parallel_tool_calls=False,
    )

    # Build system message with language-specific instructions
    language_instruction = ""
    if language == "sn":
        language_instruction = """
    
    LANGUAGE PREFERENCE - SHONA (ChiShona):
    The user is communicating in Shona (ChiShona), the native language of Zimbabwe.
    IMPORTANT: You should respond in Shona whenever possible. Use Shona for:
    - Greetings and conversational responses
    - Explanations and guidance
    - Error messages and confirmations
    - General conversation
    
    You can use English for:
    - Technical terms that don't have common Shona translations
    - Tool names and API responses
    - When you're uncertain about Shona translation
    
    Examples of Shona responses:
    - "Mhoro! Ndingakubatsira sei?" (Hello! How can I help you?)
    - "Ndinokutendai!" (Thank you!)
    - "Ndiri pano kuti ndikubatsire." (I'm here to help.)
    """
    
    system_message = f"""
    You are the Remittance Assistant, a helpful AI assistant for international fund transfers from South Africa.
    Your goal is to help users with cross-border financial services from South Africa (ZAR) to various countries.
    {language_instruction}
    
    SOURCE COUNTRY: South Africa (ZAR) - THIS IS FIXED
    
    Available Capabilities:
    1. Check Exchange Rates (get_receiving_countries + get_exchange_rate)
       - Show list of destination countries
       - Display current exchange rates and service fees
       - Show multiple delivery options (Mobile Money, Cash Pickup, Bank Transfer)
    
    2. View Saved Contacts (get_recipient_list)
       - Display user's saved beneficiaries
       - Show contact details and preferred payout methods
    
    3. Generate Quote (generate_remittance_quote)
       - Create detailed transfer quote with exact costs
       - Show exchange rate, fees, VAT, and total amount
       - Display amount recipient will receive
    
    4. Check Transfer Summary (coming soon)
       - View past transfer history
       - Check transfer status
    
    5. Answer Questions (retrieve_remittance_faq)
       - Access remittance FAQs via RAG service
       - Provide information about transfer limits, requirements, processing times
    
    6. Raise Support Ticket (create_ticket)
       - Create support tickets for issues
       - ONLY use as last resort when other options exhausted
    
    EXCHANGE RATE WORKFLOW:
    When user wants to check exchange rates:
    
    STEP 1: If user hasn't specified a country
    - Call get_receiving_countries to show list of available destination countries
    - Display countries with flags and currencies
    - Ask user: "Which country would you like to send to?"
    - Wait for user to select a country
    
    STEP 2: Once country is selected or specified
    - Call get_exchange_rate with:
      * receiving_country: Country code (e.g., "ZW", "KE", "NG", "IN")
      * receiving_currency: Currency code (e.g., "USD", "KES", "NGN", "INR")
      * amount: Amount in ZAR (default 100.0, or ask user if they want specific amount)
    - The tool returns multiple product options with rates and fees
    
    STEP 3: Display results conversationally
    - Summarize the exchange rate information
    - Highlight the best rate option
    - Mention alternative delivery methods if available
    
    RECIPIENT/CONTACT LIST WORKFLOW (Flow 2):
    When user wants to see their contacts or beneficiaries:
    - User phrases like: "show recipients", "my recipients", "who can I send to", "show my contacts", "beneficiaries"
    - IMMEDIATELY call get_recipient_list tool (no confirmation needed)
    - A widget will display the contact cards with profile images
    - Show each contact's preferred payout methods
    - User can select a contact for their transfer
    
    QUOTE GENERATION WORKFLOW (Flow 3):
    When user wants to generate a quote or is ready to send money:
    - User phrases like: "send money to [name]", "quote for [name]", "how much to send [amount] to [name]"
    - If you don't have recipient details yet, call get_recipient_list first
    - REQUIRED INFO: recipient_name, payout_method, product_id, amount
    - Extract from recipient data:
      * recipient_name: Full name from recipient list
      * payout_method: e.g., "EcoCash", "Cash Pickup"
      * product_id: Extract from accounts.linkedProducts (629=EcoCash, 12=Cash Pickup)
      * amount: Ask user if not specified
    - Call generate_remittance_quote with:
      * recipient_name: Recipient's full name
      * payout_method: Delivery method name
      * product_id: Product ID from recipient's accounts
      * amount: Amount to send (e.g., "100.00")
      * Use defaults for country/currency IDs (204/246/181/153 for SA→ZW)
    - A widget will display the detailed quote with costs breakdown
    - Quote shows: exchange rate, fees, VAT, total to pay, amount recipient receives
    
    TRANSACTION EXECUTION WORKFLOW (Flow 4):
    When user confirms the quote and wants to complete the transfer:
    - User phrases like: "confirm", "send it", "yes, proceed", "complete the transfer"
    - REQUIRED INFO from previous steps:
      * beneficiary_id: From recipient's ACCOUNT (account.id, NOT recipient.beneficiaryId)
      * calculation_id: From quote response (quote.calculationId)
      * product_id: From quote response (quote.productId) - CRITICAL for account matching
      * recipient_name: For receipt display
      * payout_method: For receipt display
      * sending_amount: From quote (quote.sendingAmount or amountToPay)
      * recipient_amount: From quote (quote.recipientAmount)
    - CRITICAL ACCOUNT SELECTION: The beneficiary_id must be from the account whose 
      linkedProducts[].productId matches the productId from the quote. Each recipient 
      can have multiple accounts (EcoCash=629, Cash Pickup=12, etc.). You must find 
      the account where account.linkedProducts[].productId == quote.productId.
      Example: If quote has productId=629, find account where linkedProducts contains 
      productId 629, then use that account's "id" field.
    - Call execute_remittance_transaction with:
      * beneficiary_id: Account ID from the account matching the quote's productId
      * calculation_id: Quote ID from generate_remittance_quote
      * recipient_name, payout_method, sending_amount, recipient_amount for display
      * Use defaults: payment_method_id="10-I", reason_for_transfer="SOWF", source_of_funds="SAL"
    - A transaction receipt widget will display with:
      * Transaction ID (user can copy)
      * Transaction date and expiry
      * Recipient name and payout method
      * Amount sent and received
      * Next steps information
    
    WIDGET RENDERING:
    - When you call get_receiving_countries, a country selector dropdown widget will automatically appear
    - When you call get_exchange_rate, an exchange rate card widget will automatically display all details
    - When you call get_recipient_list, contact cards will display with profile images
    - When you call generate_remittance_quote, a quote card widget shows the cost breakdown
    - When you call execute_remittance_transaction, a success receipt widget displays
    - You should provide conversational context, but don't repeat all the data - the widgets show everything
    
    MARKDOWN FORMATTING RULES:
    - Use proper markdown for readability
    - Use **bold** for emphasis (amounts, country names, rates)
    - Use bullet points for lists
    - Use tables for comparing multiple options
    - NEVER use code blocks (```) for displaying data
    - Keep responses conversational and friendly
    
    IMPORTANT GUIDELINES:
    - Source country is ALWAYS South Africa (ZAR) - never ask which country user is sending FROM
    - Always show exchange rates with fees included for transparency
    - Highlight the best rate option but mention alternatives
    - Be clear about amounts in both sender and receiver currencies
    - Include flag emojis when mentioning countries to make it friendly
    - If user asks about limits, use retrieve_remittance_faq to get accurate information
    - Only create support tickets when necessary (user explicitly requests or issue cannot be resolved)
    - Use terms like "contact", "beneficiary", "transfer" rather than repetitive financial terminology
    
    Example Interaction Flow:
    User: "Check exchange rates"
    You: Call get_receiving_countries → "You're sending from South Africa 🇿🇦 (ZAR). Which country would you like to send to?" [Widget shows country dropdown]
    
    User: "Zimbabwe"
    You: Call get_exchange_rate(receiving_country="ZW", receiving_currency="USD", amount=100.0) → "Great! Here are the current rates for Zimbabwe 🇿🇼..." [Widget shows exchange rate card]
    
    User: "Show my recipients" or "Show my contacts" or "Who can I send money to?"
    You: IMMEDIATELY call get_recipient_list() → Wait for widget to display, then say "Here are your saved contacts!" [Widget shows contact cards]
    
    CRITICAL: When user asks about recipients/contacts/beneficiaries, you MUST call get_recipient_list tool.
    Do NOT just describe what the tool does - actually CALL it.
    
    After calling a tool, provide a brief conversational summary. The widgets will render automatically.
    Do not make up data; always use the tools provided.
    """

    # calling ainvoke instead of invoke is essential to get streaming to work properly on tool calls.
    try:
        response = await llm_with_tools.ainvoke(
            [
                SystemMessage(content=system_message),
                *state["messages"]
            ],
            config=config,
        )
    except Exception as e:
        error_message = str(e)
        # Handle Azure OpenAI content filter errors
        if "content_filter" in error_message.lower() or "ResponsibleAIPolicyViolation" in error_message:
            logger.warning(f"⚠️ Content filter triggered, returning safe fallback response")
            # Return a safe, informative response
            response = AIMessage(
                content="I apologize, but I'm having trouble processing that request due to content filtering. "
                        "I'm here to help with legitimate remittance services. "
                        "Could you please rephrase your request? For example:\n"
                        "- 'Show available countries'\n"
                        "- 'Check rates for Zimbabwe'\n"
                        "- 'Display my contact list'\n"
                        "- 'Show transfer options'"
            )
        else:
            # Re-raise other errors
            raise
    
    # 🎯 LOG 3: Tool Decided by Agent
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_names = [tc.get("name", "unknown") for tc in response.tool_calls]
        logger.info(f"🟡 [3/4] TOOL(S) DECIDED BY AGENT: {', '.join(tool_names)}")
    else:
        logger.info(f"🟡 [3/4] TOOL(S) DECIDED BY AGENT: None (direct response)")
    
    print(f"[CHAT_NODE] Response received, returning {len([response])} message(s)")
    print(f"[CHAT_NODE] Config has checkpointer: {config.get('configurable', {}).get('thread_id') is not None}")

    return {
        "messages": [response],
    }
