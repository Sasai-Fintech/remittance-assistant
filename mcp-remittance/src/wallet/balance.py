"""Wallet balance operations for FastMCP server."""

import sys
from typing import Literal, Dict, Any, Optional

from config.settings import SasaiConfig
from api.client import SasaiAPIClient
from auth.manager import token_manager
from auth.tools import generate_authentication_token


def register_balance_tools(mcp_server) -> None:
    """
    Register wallet balance tools with the MCP server.
    
    Args:
        mcp_server: FastMCP server instance
    """
    
    @mcp_server.tool
    async def get_wallet_balance(
        currency: Literal["USD", "EUR", "GBP", "ZWL"] = "USD",
        provider_code: Literal["remittance", "onemoney", "telecash"] = "remittance",
        auto_generate_token: bool = True,
        external_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch wallet balance from Sasai Payment Gateway.
        
        This tool retrieves the current wallet balance for a specified currency and payment provider
        from the Sasai Payment Gateway sandbox environment.
        
        Args:
            currency: The currency code for the balance inquiry (USD, EUR, GBP, ZWL)
            provider_code: The payment provider code (remittance, onemoney, telecash)
            auto_generate_token: Whether to automatically generate a new token if none exists (only if token manager is enabled)
            external_token: Optional external authentication token (used when token manager is disabled)
        
        Returns:
            dict: Wallet balance information including:
                - balance: Current balance amount
                - currency: Currency code
                - provider: Provider information
                - status: Transaction status
                - timestamp: Response timestamp
        
        Raises:
            AuthenticationError: If authentication is required but token is missing
            SasaiAPIError: If the API request fails or returns an error
        """
        # Get token - external token ALWAYS takes precedence over token manager
        token = None
        if external_token:
            token = external_token
            print(f"[BALANCE_API] ✅ Using EXTERNAL token (preview): {token[:20] if token else 'None'}...", flush=True)
            print(f"[BALANCE_API] External token takes precedence over token manager", flush=True)
        elif token_manager.is_enabled():
            # Check if we need to generate a token
            if not token_manager.has_token() and auto_generate_token:
                print(f"[BALANCE_API] No external token provided, generating new token via token manager...", flush=True)
                token_result = await generate_authentication_token()
                if not token_result.get("success"):
                    raise Exception("Failed to generate authentication token")
            token = token_manager.get_token()
            print(f"[BALANCE_API] Using token manager token (preview): {token[:20] if token else 'None'}...", flush=True)
        else:
            # Token manager is disabled and no external token provided
            raise Exception("Token manager is disabled. Please provide external_token parameter.")
        
        # Prepare query parameters
        params = {
            "currency": currency,
            "providerCode": provider_code
        }
        
        # Log the API call details
        endpoint = SasaiConfig.ENDPOINTS.wallet_balance
        token_preview = token[:20] + "..." if token else "None"
        
        print(f"[BALANCE_API] Making GET request to: {endpoint}", flush=True)
        print(f"[BALANCE_API] Query parameters: {params}", flush=True)
        print(f"[BALANCE_API] Token (preview): {token_preview}", flush=True)
        print(f"[BALANCE_API] Currency: {currency}, Provider: {provider_code}", flush=True)
        
        # Make the API request using the API client
        client = SasaiAPIClient()
        result = await client.get(
            endpoint=endpoint,
            token=token,
            params=params,
            require_auth=True
        )
        
        # Log the response
        print(f"[BALANCE_API] Response status: {result.get('status_code', 'N/A')}", flush=True)
        print(f"[BALANCE_API] Response success: {result.get('success', False)}", flush=True)
        if result.get('data'):
            balance_data = result.get('data', {})
            print(f"[BALANCE_API] Balance data keys: {list(balance_data.keys()) if isinstance(balance_data, dict) else 'N/A'}", flush=True)
        
        # Enhance response with request metadata
        result["request_info"] = {
            "currency": currency,
            "provider_code": provider_code,
            "tool": "get_wallet_balance"
        }
        
        return result
