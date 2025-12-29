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
    Calculate locked-in rate for selected vendor and generate calculationId.
    
    This is Step 2 in the remittance flow: After user selects a delivery method
    (vendor) from the exchange rate options, this function locks in that rate
    and generates a calculationId that will be used to create the quote.
    
    Flow Context:
    - Step 1: get_exchange_rate shows multiple vendor options
    - Step 2: THIS FUNCTION - Lock rate and get calculationId
    - Step 3: generate_quote uses calculationId to create quote with transactionId
    - Step 4: execute_transaction uses transactionId to complete transfer
    
    This provides a detailed breakdown of:
    - Exchange rate and reverse rate
    - Sending amount and receiving amount  
    - Transaction fees and VAT
    - Total amount to pay
    - **calculationId** - Used in next step to generate quote
    
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
        dict: Rate calculation details with:
            - calculationId: Unique calculation ID (CRITICAL - used in Step 3)
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
        logger.info(f"[CALCULATE_RATE] Step 2: Calculating rate for amount={amount}, product={product_id}")
        
        # Get or generate authentication token
        token = token_manager.get_token()
        
        if not token:
            logger.info("[CALCULATE_RATE] No token available, generating new token...")
            token_result = await generate_authentication_token(ctx=ctx)
            
            if not token_result.get("success"):
                error_msg = token_result.get("error", "Unknown authentication error")
                logger.error(f"[CALCULATE_RATE] Authentication failed: {error_msg}")
                return {
                    "success": False,
                    "error": f"Authentication failed: {error_msg}"
                }
            
            token = token_result.get("token")
            logger.info("[CALCULATE_RATE] Successfully generated new token")
        
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
        
        logger.info(f"[CALCULATE_RATE] Request payload: {payload}")
        
        # Make API call to Step 2 endpoint
        client = SasaiAPIClient()
        response = await client.calculate_rate(token=token, payload=payload)
        
        logger.info(f"[CALCULATE_RATE] API Response: {response}")
        
        return response
        
    except Exception as e:
        logger.error(f"[CALCULATE_RATE] Error calculating rate: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to calculate rate: {str(e)}"
        }


async def generate_remittance_quote_from_calculation(
    beneficiary_id: str,
    calculation_id: str,
    payment_method_id: str = "10-I",
    reason_for_transfer: str = "SOWF",
    source_of_funds: str = "SAL",
    ctx: Context | None = None
) -> dict[str, Any]:
    """
    Generate quote using calculationId from rate calculation.
    
    This is Step 3 in the remittance flow: Uses the calculationId from Step 2
    to generate a quote with the locked-in rate and returns a transactionId.
    
    Flow Context:
    - Step 1: get_exchange_rate shows multiple vendor options
    - Step 2: calculate_remittance_quote locks rate and gets calculationId
    - Step 3: THIS FUNCTION - Generate quote and get transactionId
    - Step 4: execute_transaction uses transactionId to complete transfer
    
    CRITICAL: beneficiary_id must be from the ACCOUNT that matches the product!
    
    HOW TO SELECT THE CORRECT ACCOUNT:
    1. Get productId from the rate calculation response
    2. Find the account in recipient.accounts[] where:
       account.linkedProducts[].productId == calculation.productId
    3. Use that account's "id" field as the beneficiary_id parameter
    
    Example from get_recipient_list API response:
    {
      "beneficiaryId": "12345",  // <-- Don't use this top-level field
      "firstName": "John",
      "accounts": [
        {
          "id": "77192529",  // <-- Use THIS if productId = 629
          "beneficiaryPayoutMethod": "EcoCash",
          "linkedProducts": [{"productId": 629, "accountName": "EcoCash"}]
        },
        {
          "id": "77192530",  // <-- Use THIS if productId = 12
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
        calculation_id: Calculation ID from rate calculation (Step 2)
        payment_method_id: Payment method ID (default: "10-I")
        reason_for_transfer: Reason code (default: "SOWF" - Support of Family)
        source_of_funds: Source code (default: "SAL" - Salary)
        ctx: MCP context (optional)
        
    Returns:
        dict: Quote with transactionId:
            - transactionId: Unique transaction ID (CRITICAL - used in Step 4)
            - transactionDate: When quote was created
            - expiryDate: When quote expires
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
        logger.info(f"[GENERATE_QUOTE] Step 3: Generating quote for beneficiary={beneficiary_id}, calculation={calculation_id}")
        
        # Get or generate authentication token
        token = token_manager.get_token()
        
        if not token:
            logger.info("[GENERATE_QUOTE] No token available, generating new token...")
            token_result = await generate_authentication_token(ctx=ctx)
            
            if not token_result.get("success"):
                error_msg = token_result.get("error", "Unknown authentication error")
                logger.error(f"[GENERATE_QUOTE] Authentication failed: {error_msg}")
                return {
                    "success": False,
                    "error": f"Authentication failed: {error_msg}"
                }
            
            token = token_result.get("token")
            logger.info("[GENERATE_QUOTE] Successfully generated new token")
        
        # Prepare request payload for Step 3
        payload = {
            "reasonForTransfer": reason_for_transfer,
            "sourceOfFunds": source_of_funds,
            "beneficiaryId": beneficiary_id,
            "calculationId": calculation_id,
            "paymentMethodId": payment_method_id,
        }
        
        logger.info(f"[GENERATE_QUOTE] Request payload: {payload}")
        
        # Make API call to Step 3 endpoint (POST /v1/transaction)
        client = SasaiAPIClient()
        response = await client.generate_quote(token=token, payload=payload)
        
        logger.info(f"[GENERATE_QUOTE] API Response: {response}")
        
        return response
        
    except Exception as e:
        logger.error(f"[GENERATE_QUOTE] Error generating quote: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to generate quote: {str(e)}"
        }
