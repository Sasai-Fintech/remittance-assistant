"""
Payment Options Module for Remittance Assistant.

This module provides tools for retrieving available payment methods
before executing a transaction.
"""

import logging
from typing import Any, Optional

from api.client import SasaiAPIClient
from auth.manager import token_manager
from auth.tools import generate_authentication_token

logger = logging.getLogger(__name__)


async def get_payment_options(
    service_type: str = "ZAPersonPaymentOptions",
    ctx: Any | None = None
) -> dict[str, Any]:
    """
    Get available payment options for transaction execution.
    
    This is Step 4a in the remittance flow: After quote confirmation, show
    the user available payment methods to complete the transaction.
    
    Flow Context:
    - Step 1: get_exchange_rate shows multiple vendor options
    - Step 2: calculate_remittance_quote locks rate and gets calculationId
    - Step 3: generate_remittance_quote_from_calculation creates quote and gets transactionId
    - Step 4a: THIS FUNCTION - Get available payment methods
    - Step 4b: execute_remittance_transaction - Complete transaction with selected method
    
    Args:
        service_type: Service type for payment options (default: "ZAPersonPaymentOptions")
        ctx: MCP context (optional)
        
    Returns:
        dict: Payment options with method details
        
    Example Response:
        {
            "success": true,
            "paymentOptions": [
                {
                    "code": "EFT",
                    "name": "Electronic Funds Transfer",
                    "description": "Bank transfer from your account",
                    "icon": "bank"
                },
                {
                    "code": "CARD",
                    "name": "Debit/Credit Card",
                    "description": "Pay with your card",
                    "icon": "card"
                },
                {
                    "code": "WALLET",
                    "name": "Mobile Wallet",
                    "description": "Pay from your mobile wallet",
                    "icon": "wallet"
                }
            ]
        }
    """
    try:
        logger.info(f"[GET_PAYMENT_OPTIONS] Step 4a: Getting payment options")
        logger.info(f"[GET_PAYMENT_OPTIONS] Service type: {service_type}")
        
        # Get or generate authentication token
        token = token_manager.get_token()
        
        if not token:
            logger.info("[GET_PAYMENT_OPTIONS] No token available, generating new token...")
            token_result = await generate_authentication_token(ctx=ctx)
            
            if not token_result.get("success"):
                error_msg = token_result.get("error", "Unknown authentication error")
                logger.error(f"[GET_PAYMENT_OPTIONS] Authentication failed: {error_msg}")
                return {
                    "success": False,
                    "error": f"Authentication failed: {error_msg}"
                }
            
            token = token_result.get("token")
            logger.info("[GET_PAYMENT_OPTIONS] Successfully generated new token")
        
        # Make API call to get payment options
        client = SasaiAPIClient()
        response = await client.get_payment_options(token=token, service_type=service_type)
        
        logger.info(f"[GET_PAYMENT_OPTIONS] Raw API Response: {response}")
        
        # Transform API response to widget format
        if response and isinstance(response, dict):
            items = response.get("items", [])
            
            # Transform items into payment options format expected by widget
            payment_options = []
            for item in items:
                code = item.get("code", "")
                value = item.get("value", "")
                icon_url = item.get("iconUrl", "")
                
                # Map icons
                icon_map = {
                    "eft": "bank",
                    "cash": "wallet",
                    "card": "card"
                }
                icon = icon_map.get(code.lower(), "payment")
                
                # Create payment option
                payment_option = {
                    "code": code,
                    "name": value,
                    "description": f"Pay using {value}",
                    "icon": icon,
                    "iconUrl": icon_url
                }
                payment_options.append(payment_option)
            
            logger.info(f"[GET_PAYMENT_OPTIONS] Transformed {len(payment_options)} payment options")
            
            return {
                "success": True,
                "paymentOptions": payment_options,
                "raw": response  # Keep raw response for debugging
            }
        
        return response
        
    except Exception as e:
        logger.error(f"[GET_PAYMENT_OPTIONS] Error getting payment options: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get payment options: {str(e)}"
        }
