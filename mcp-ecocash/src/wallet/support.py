"""Support ticket operations for FastMCP server."""

from typing import Dict, Any, Literal, Optional

from config import SasaiConfig
from api import SasaiAPIClient
from auth.manager import token_manager
from auth.tools import generate_authentication_token


def register_support_tools(mcp_server) -> None:
    """
    Register support ticket tools with the MCP server.
    
    Args:
        mcp_server: FastMCP server instance
    """
    
    @mcp_server.tool
    async def create_support_ticket(
        name: str,
        phone: str,
        subject: str,
        type: Literal["Logged a Transaction", "Updated Client Details", "Updated Beneficiary Details", "General Enquiry"] = "General Enquiry",
        description: str = "",
        auto_generate_token: bool = True,
        external_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a support ticket for the user.
        
        This tool creates a support ticket with the Sasai Payment Gateway API.
        
        Args:
            name: Name of the user creating the ticket
            phone: Phone number of the user (format: +countrycode+number, e.g., +918920673899)
            subject: Subject/title of the ticket
            type: Type of ticket. Valid values:
                - "Logged a Transaction": For issues related to a specific transaction
                - "Updated Client Details": For issues related to client profile updates
                - "Updated Beneficiary Details": For issues related to beneficiary information
                - "General Enquiry": For general questions or other issues (default)
            description: Detailed description of the issue
            auto_generate_token: Whether to automatically generate a new token if none exists (only if token manager is enabled)
            external_token: Optional external authentication token (used when token manager is disabled)
        
        Returns:
            dict: Ticket creation result including:
                - success: Whether the ticket was created successfully
                - ticket_id: The created ticket ID
                - message: Response message from the API
        """
        # Get token - use external token if provided, otherwise use token manager
        token = None
        if external_token:
            token = external_token
            print(f"[SUPPORT_API] Using external token (preview): {token[:20] if token else 'None'}...", flush=True)
        elif token_manager.is_enabled():
            # Check if we need to generate a token
            if not token_manager.has_token() and auto_generate_token:
                token_result = await generate_authentication_token()
                if not token_result.get("success"):
                    raise Exception("Failed to generate authentication token")
            token = token_manager.get_token()
        else:
            # Token manager is disabled and no external token provided
            raise Exception("Token manager is disabled. Please provide external_token parameter.")
        
        # Prepare JSON payload
        json_payload = {
            "name": name,
            "phone": phone,
            "subject": subject,
            "type": type,
            "description": description
        }
        
        # Make the API request using the API client
        client = SasaiAPIClient()
        result = await client.post(
            endpoint=SasaiConfig.ENDPOINTS.support_ticket,
            token=token,
            json_data=json_payload,
            require_auth=True
        )
        
        # Log the response
        print(f"[SUPPORT_API] Create ticket response status: {result.get('status_code', 'N/A')}", flush=True)
        print(f"[SUPPORT_API] Create ticket response success: {result.get('success', False)}", flush=True)
        if result.get('data'):
            data = result.get('data', {})
            print(f"[SUPPORT_API] Ticket data keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}", flush=True)
        
        # Enhance response with request metadata
        result["request_info"] = {
            "tool": "create_support_ticket",
            "name": name,
            "phone": phone,
            "subject": subject,
            "type": type
        }
        
        return result
    
    @mcp_server.tool
    async def list_support_tickets(
        auto_generate_token: bool = True,
        external_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all support tickets for the authenticated user.
        
        This tool retrieves a list of all support tickets associated with the current user.
        
        Args:
            auto_generate_token: Whether to automatically generate a new token if none exists (only if token manager is enabled)
            external_token: Optional external authentication token (used when token manager is disabled)
        
        Returns:
            dict: List of support tickets including:
                - success: Whether the request was successful
                - tickets: List of ticket objects
                - total_count: Total number of tickets
        """
        # Get token - use external token if provided, otherwise use token manager
        token = None
        if external_token:
            token = external_token
            print(f"[SUPPORT_API] Using external token (preview): {token[:20] if token else 'None'}...", flush=True)
        elif token_manager.is_enabled():
            # Check if we need to generate a token
            if not token_manager.has_token() and auto_generate_token:
                token_result = await generate_authentication_token()
                if not token_result.get("success"):
                    raise Exception("Failed to generate authentication token")
            token = token_manager.get_token()
        else:
            # Token manager is disabled and no external token provided
            raise Exception("Token manager is disabled. Please provide external_token parameter.")
        
        # Make the API request using the API client (GET request)
        client = SasaiAPIClient()
        result = await client.get(
            endpoint=SasaiConfig.ENDPOINTS.support_ticket,
            token=token,
            require_auth=True
        )
        
        # Log the response
        print(f"[SUPPORT_API] List tickets response status: {result.get('status_code', 'N/A')}", flush=True)
        print(f"[SUPPORT_API] List tickets response success: {result.get('success', False)}", flush=True)
        if result.get('data'):
            data = result.get('data', {})
            print(f"[SUPPORT_API] Tickets data type: {type(data)}", flush=True)
            if isinstance(data, dict):
                print(f"[SUPPORT_API] Tickets data keys: {list(data.keys())}", flush=True)
                # Check for tickets array
                if 'tickets' in data or isinstance(data.get('tickets'), list):
                    tickets_list = data.get('tickets', [])
                    print(f"[SUPPORT_API] Found {len(tickets_list)} tickets", flush=True)
            elif isinstance(data, list):
                print(f"[SUPPORT_API] Data is a list with {len(data)} tickets", flush=True)
        
        # Enhance response with request metadata
        result["request_info"] = {
            "tool": "list_support_tickets"
        }
        
        return result
