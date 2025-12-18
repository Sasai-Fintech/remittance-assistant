"""
Quote/Rate Calculation Module for Remittance Assistant.

This module provides tools for calculating remittance quotes including
exchange rates, fees, and total amounts.
"""

import logging
from typing import Any, Optional
from fastmcp import Context

from api.client import SasaiAPIClient
from auth.manager import token_manager
from auth.tools import generate_authentication_token

logger = logging.getLogger(__name__)


async def calculate_remittance_quote(
    sending_country_id: int,
    receiving_country_id: int,
    sending_currency_id: int,
    receiving_currency_id: int,
    amount: str,
    product_id: int,
    payment_method_id: str = "5",
    receive: bool = False,
    spg_order_id: Optional[str] = None,
    notes: Optional[dict] = None,
    ctx: Context | None = None
) -> dict[str, Any]:
    """
    Calculate remittance quote with exchange rate, fees, and total amount.
    
    This provides a detailed breakdown of:
    - Exchange rate and reverse rate
    - Sending amount and receiving amount
    - Transaction fees and VAT
    - Total amount to pay
    
    Common Parameters:
    - sending_country_id: 204 (South Africa)
    - receiving_country_id: 246 (Zimbabwe)
    - sending_currency_id: 181 (ZAR - South African Rand)
    - receiving_currency_id: 153 (USD - US Dollar)
    - product_id: 629 (EcoCash), 12 (Cash Pickup)
    - payment_method_id: "5" (default payment method)
    
    Args:
        sending_country_id: ID of the country sending money from (e.g., 204 for South Africa)
        receiving_country_id: ID of the country receiving money (e.g., 246 for Zimbabwe)
        sending_currency_id: ID of the sending currency (e.g., 181 for ZAR)
        receiving_currency_id: ID of the receiving currency (e.g., 153 for USD)
        amount: Amount to send/receive as string (e.g., "100.00")
        product_id: Payout product ID (629=EcoCash, 12=Cash Pickup)
        payment_method_id: Payment method ID (default: "5")
        receive: If True, amount is what recipient receives; if False, amount is what sender sends
        spg_order_id: Optional order ID for tracking
        notes: Optional notes dict (e.g., {"subtype": "tip"})
        ctx: MCP context (optional)
        
    Returns:
        dict: Quote details with:
            - calculationId: Unique calculation ID
            - calculateId: Hash for this calculation
            - sendingAmount: Amount sender pays (before fees)
            - recipientAmount: Amount recipient receives
            - rate: Exchange rate (sending to receiving)
            - reverseRate: Reverse exchange rate
            - fees: Transaction fees
            - vat: Value-added tax
            - surcharges: Additional charges
            - amountToPay: Total amount sender must pay (including fees)
            
    Example Response:
        {
            "calculationId": "3cb87ef2-004f-4b74-9acb-527ffea1f512",
            "sendingAmount": "100.00",
            "recipientAmount": "6.64",
            "rate": "0.0664",
            "reverseRate": "15.0602",
            "fees": "1.73",
            "vat": "0.23",
            "amountToPay": "101.73"
        }
    """
    try:
        logger.info(f"[CALCULATE_QUOTE] Calculating quote for amount={amount}, product={product_id}")
        
        # Get or generate authentication token
        token = token_manager.get_token()
        
        if not token:
            logger.info("[CALCULATE_QUOTE] No token available, generating new token...")
            token_result = await generate_authentication_token(ctx=ctx)
            
            if not token_result.get("success"):
                error_msg = token_result.get("error", "Unknown authentication error")
                logger.error(f"[CALCULATE_QUOTE] Authentication failed: {error_msg}")
                return {
                    "success": False,
                    "error": f"Authentication failed: {error_msg}"
                }
            
            token = token_result.get("token")
            logger.info("[CALCULATE_QUOTE] Successfully generated new token")
        
        # Prepare request payload
        payload = {
            "sendingCountryId": sending_country_id,
            "receivingCountryId": receiving_country_id,
            "sendingCurrencyId": sending_currency_id,
            "receivingCurrencyId": receiving_currency_id,
            "amount": amount,
            "productId": product_id,
            "receive": receive,
            "paymentMethodId": payment_method_id,
        }
        
        # Add optional fields
        if spg_order_id:
            payload["spgOrderId"] = spg_order_id
        if notes:
            payload["notes"] = notes
        
        logger.info(f"[CALCULATE_QUOTE] Request payload: {payload}")
        
        # Make API call
        client = SasaiAPIClient()
        response = await client.calculate_rate(token=token, payload=payload)
        
        logger.info(f"[CALCULATE_QUOTE] API Response: {response}")
        
        return response
        
    except Exception as e:
        logger.error(f"[CALCULATE_QUOTE] Error calculating quote: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to calculate quote: {str(e)}"
        }
