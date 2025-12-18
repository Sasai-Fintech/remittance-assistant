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
    beneficiary_id: str,
    calculation_id: str,
    payment_method_id: str = "10-I",
    reason_for_transfer: str = "SOWF",
    source_of_funds: str = "SAL",
    ctx: Context | None = None
) -> dict[str, Any]:
    """
    Execute a remittance transaction after quote confirmation.
    
    This completes the money transfer by:
    - Creating the transaction with the beneficiary account
    - Using the locked-in quote from calculation
    - Processing the payment
    - Returning transaction receipt
    
    CRITICAL: beneficiary_id must be from the account that matches the quote's productId!
    
    HOW TO SELECT THE CORRECT ACCOUNT:
    1. Get productId from the quote response (e.g., 629 for EcoCash)
    2. Find the account in recipient.accounts[] where:
       account.linkedProducts[].productId == quote.productId
    3. Use that account's "id" field as the beneficiary_id parameter
    
    Example from get_recipient_list API response:
    {
      "beneficiaryId": "12345",  // <-- Don't use this top-level field
      "firstName": "John",
      "accounts": [
        {
          "id": "77192529",  // <-- Use THIS if quote.productId = 629
          "beneficiaryPayoutMethod": "EcoCash",
          "linkedProducts": [{"productId": 629, "accountName": "EcoCash"}]
        },
        {
          "id": "77192530",  // <-- Use THIS if quote.productId = 12
          "beneficiaryPayoutMethod": "Cash Pickup",
          "linkedProducts": [{"productId": 12, "accountName": "Cash"}]
        }
      ]
    }
    
    Common Parameters:
    - reason_for_transfer: "SOWF" (Support of Family), "GIFT" (Gift), etc.
    - source_of_funds: "SAL" (Salary), "SAV" (Savings), "BUS" (Business), etc.
    - payment_method_id: "10-I" (default payment method)
    
    Args:
        beneficiary_id: Account ID where account.linkedProducts[].productId matches quote.productId
        calculation_id: Quote calculation ID from generate_remittance_quote
        payment_method_id: Payment method ID (default: "10-I")
        reason_for_transfer: Reason code (default: "SOWF" - Support of Family)
        source_of_funds: Source code (default: "SAL" - Salary)
        ctx: MCP context (optional)
        
    Returns:
        dict: Transaction receipt with:
            - transactionId: Unique transaction ID
            - transactionDate: When transaction was created
            - expiryDate: When transaction expires
            - promocode: Applied promo code (if any)
            
    Example Response:
        {
            "transactionId": "71866575",
            "transactionDate": "2025-12-17 15:02:26",
            "expiryDate": "2025-12-18 15:02:26",
            "promocode": null
        }
    """
    try:
        logger.info(f"[EXECUTE_TRANSACTION] Executing transaction for beneficiary={beneficiary_id}, calculation={calculation_id}")
        
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
        
        # Prepare request payload
        payload = {
            "reasonForTransfer": reason_for_transfer,
            "sourceOfFunds": source_of_funds,
            "beneficiaryId": beneficiary_id,
            "calculationId": calculation_id,
            "paymentMethodId": payment_method_id,
        }
        
        logger.info(f"[EXECUTE_TRANSACTION] Request payload: {payload}")
        
        # Make API call
        client = SasaiAPIClient()
        response = await client.execute_transaction(token=token, payload=payload)
        
        logger.info(f"[EXECUTE_TRANSACTION] API Response: {response}")
        
        return response
        
    except Exception as e:
        logger.error(f"[EXECUTE_TRANSACTION] Error executing transaction: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to execute transaction: {str(e)}"
        }
