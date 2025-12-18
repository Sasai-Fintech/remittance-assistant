"""
Recipient Management Module for Remittance Assistant.

This module provides tools for managing recipients (beneficiaries) 
for remittance transactions.
"""

import logging
from typing import Any, Optional
from fastmcp import Context

from api.client import SasaiAPIClient
from auth.manager import token_manager

logger = logging.getLogger(__name__)


async def get_recipient_list(
    page: int = 1,
    count: int = 20,
    ctx: Context | None = None
) -> dict[str, Any]:
    """
    Fetch list of saved recipients/beneficiaries for the user.
    
    Each recipient can have multiple payout methods (accounts):
    - Cash Pickup: Physical cash collection
    - Mobile Money: EcoCash, Mukuru, etc.
    - Bank Transfer: Bank account deposits
    
    Args:
        page: Page number for pagination (default: 1)
        count: Number of items per page (default: 20, max: 50)
        ctx: MCP context (optional)
        
    Returns:
        dict: Recipient list with:
            - items: List of recipients with their details and accounts
            - total: Total number of recipients
            - page: Current page number
            - count: Items per page
            
    Example Response:
        {
            "items": [
                {
                    "firstName": "John",
                    "lastName": "Doe",
                    "mobile": "712345678",
                    "countryIsdCode": "263",
                    "relationship": "BR",
                    "relationshipValue": "Brother",
                    "beneficiaryId": "abc123...",
                    "accounts": [
                        {
                            "id": "12345",
                            "beneficiaryPayoutMethod": "EcoCash (263 712345678)",
                            "mobileMoneyProvider": "EcoCash",
                            "nickname": "John's EcoCash",
                            "linkedProducts": [{"productId": 629, "accountName": "..."}]
                        }
                    ],
                    "isSasaiUser": true,
                    "profileImage": "https://...",
                    "customerId": "def456..."
                }
            ],
            "total": 155,
            "page": 1,
            "count": 20
        }
    """
    try:
        # Get authentication token
        token = token_manager.get_token()
        
        # If no token, generate one
        if not token:
            from auth.tools import generate_authentication_token
            token_result = await generate_authentication_token()
            
            if not token_result.get("success"):
                logger.error(f"[GET_RECIPIENT_LIST] Failed to generate token: {token_result.get('message')}")
                return {
                    "error": "Authentication failed",
                    "message": "Unable to generate authentication token. Please try again.",
                    "items": [],
                    "total": 0,
                    "page": page,
                    "count": count
                }
            
            token = token_result.get("token")
            logger.info("[GET_RECIPIENT_LIST] Generated new authentication token")
        else:
            logger.info("[GET_RECIPIENT_LIST] Using existing token from manager")
        
        if not token:
            return {
                "error": "Authentication failed",
                "message": "No valid token available",
                "items": [],
                "total": 0,
                "page": page,
                "count": count
            }
        
        # Initialize API client
        client = SasaiAPIClient()
        
        # Fetch recipient list from API
        response = await client.get_recipient_list(token=token, page=page, count=count)
        
        # Log the response for debugging
        logger.info(f"[GET_RECIPIENT_LIST] API Response: {response}")
        logger.info(f"[GET_RECIPIENT_LIST] Items count: {len(response.get('items', []))}")
        
        # Return the response as-is (already in correct format)
        return response
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[GET_RECIPIENT_LIST] Exception: {error_msg}")
        return {
            "error": "Failed to fetch recipients",
            "message": error_msg,
            "items": [],
            "total": 0,
            "page": page,
            "count": count
        }
