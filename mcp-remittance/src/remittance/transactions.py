"""
Transaction Execution Module for Remittance Assistant.

This module provides tools for executing remittance transactions
after quote confirmation.
"""

import logging
from typing import Any, Optional
from fastmcp import Context

from api.client import SasaiAPIClient
from auth.manager import token_manager
from auth.tools import generate_authentication_token

logger = logging.getLogger(__name__)


async def execute_remittance_transaction(
    transaction_id: str,
    payment_method_code: str,
    ctx: Context | None = None
) -> dict[str, Any]:
    """
    Complete/execute transaction using transactionId from quote.
    
    This is Step 4 in the remittance flow: Uses PATCH to finalize the transaction
    with ONLY the transactionId (from Step 3) and paymentMethodCode (from Step 4a).
    
    Flow Context:
    - Step 1: get_exchange_rate shows multiple vendor options
    - Step 2: calculate_remittance_quote locks rate and gets calculationId
    - Step 3: generate_remittance_quote_from_calculation creates quote and gets transactionId
    - Step 4a: get_payment_options shows available payment methods
    - Step 4b: THIS FUNCTION - Complete the transaction with selected payment method
    
    This completes the money transfer by:
    - Using the transactionId from the quote (Step 3)
    - Using the paymentMethodCode selected by user (Step 4a)
    - Finalizing the payment with PATCH request
    - Returning final transaction receipt and confirmation
    
    CRITICAL: The PATCH API only requires TWO fields:
    - transactionId: From Step 3 (quote generation)
    - paymentMethodCode: From Step 4a (user selected, e.g., "eft", "cash", "card")
    
    Args:
        transaction_id: Transaction ID from generate_remittance_quote_from_calculation (Step 3)
        payment_method_code: Payment method code from payment options selection (Step 4a)
        ctx: MCP context (optional)
        
    Returns:
        dict: Final transaction receipt with confirmation details
            
    Example Response:
        {
            "success": true,
            "message": "Transaction completed successfully",
            "data": {
                "transactionId": "71866575",
                "status": "completed",
                "confirmationNumber": "ABC123XYZ"
            }
        }
    """
    try:
        logger.info(f"[EXECUTE_TRANSACTION] Step 4: Completing transaction={transaction_id}")
        logger.info(f"[EXECUTE_TRANSACTION] Payment method code: {payment_method_code}")
        
        # Get or generate authentication token
        token = token_manager.get_token()
        
        if not token:
            logger.info("[EXECUTE_TRANSACTION] No token available, generating new token...")
            token_result = await generate_authentication_token(ctx=ctx)
            
            if not token_result.get("success"):
                error_msg = token_result.get("error", "Unknown authentication error")
                logger.error(f"[EXECUTE_TRANSACTION] Authentication failed: {error_msg}")
                return {
                    "success": False,
                    "error": f"Authentication failed: {error_msg}"
                }
            
            token = token_result.get("token")
            logger.info("[EXECUTE_TRANSACTION] Successfully generated new token")
        
        # Prepare request payload for Step 4 (PATCH)
        # PATCH requires ONLY TWO fields: transactionId and paymentMethodCode
        payload = {
            "transactionId": transaction_id,
            "paymentMethodCode": payment_method_code
        }
        
        logger.info(f"[EXECUTE_TRANSACTION] Request payload: {payload}")
        
        # Make API call to Step 4 endpoint (PATCH /v1/transaction)
        client = SasaiAPIClient()
        response = await client.execute_transaction(token=token, payload=payload)
        
        logger.info(f"[EXECUTE_TRANSACTION] API Response: {response}")
        
        # Extract transactionUrl from response if present
        if response and isinstance(response, dict):
            data = response.get("data", {})
            transaction_url = data.get("transactionUrl")
            
            if transaction_url:
                logger.info(f"[EXECUTE_TRANSACTION] Transaction URL found: {transaction_url}")
                # Add transactionUrl to top level for easy access
                response["transactionUrl"] = transaction_url
                response["message"] = f"Transaction initiated. Please complete payment at: {transaction_url}"
        
        return response
        
    except Exception as e:
        logger.error(f"[EXECUTE_TRANSACTION] Error executing transaction: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to execute transaction: {str(e)}"
        }
