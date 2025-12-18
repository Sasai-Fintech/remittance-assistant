"""Country and exchange rate operations for Remittance."""

from typing import Dict, Any, Optional
from config.settings import SasaiConfig
from api.client import SasaiAPIClient
from auth.manager import token_manager
import logging

logger = logging.getLogger(__name__)


def register_remittance_tools(mcp_server) -> None:
    """Register remittance-specific tools."""
    
    @mcp_server.tool()
    async def get_receiving_countries(
        auto_generate_token: bool = True,
        external_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get list of receiving countries from South Africa (ZA).
        
        Returns list of countries where money can be sent from South Africa,
        including country details and supported currencies.
        
        Args:
            auto_generate_token: Auto-generate token if needed
            external_token: External authentication token (optional)
        
        Returns:
            dict: Countries data with receivingCountries array
        """
        logger.info("[GET_RECEIVING_COUNTRIES] Tool called")
        
        # Get token
        token = None
        if external_token:
            token = external_token
            logger.info("[GET_RECEIVING_COUNTRIES] Using external token")
        elif SasaiConfig.USE_TOKEN_MANAGER:
            if auto_generate_token and not token_manager.get_token():
                from auth.tools import generate_authentication_token
                token_result = await generate_authentication_token()
                if not token_result.get("success"):
                    logger.error("[GET_RECEIVING_COUNTRIES] Failed to generate authentication token")
                    raise Exception("Failed to generate authentication token")
            token = token_manager.get_token()
            logger.info("[GET_RECEIVING_COUNTRIES] Using token from manager")
        else:
            logger.error("[GET_RECEIVING_COUNTRIES] Token manager disabled and no external token provided")
            raise Exception("Token manager disabled. Provide external_token.")
        
        # API endpoint
        endpoint = f"{SasaiConfig.BASE_URL}/remittance/v1/master/country"
        params = {"currentUpdatedAt": "0"}
        
        logger.info(f"[GET_RECEIVING_COUNTRIES] Fetching countries from: {endpoint}")
        
        # Make API request
        client = SasaiAPIClient()
        result = await client.get(
            endpoint=endpoint,
            token=token,
            params=params,
            require_auth=True
        )
        
        # Extract South Africa's receiving countries
        if result.get('success') and result.get('data'):
            items = result['data'].get('items', [])
            for country in items:
                if country.get('countryCode') == 'ZA':
                    receiving = country.get('receivingCountries', [])
                    logger.info(f"[GET_RECEIVING_COUNTRIES] Found {len(receiving)} receiving countries from South Africa")
                    return {
                        "success": True,
                        "data": {
                            "sourceCountry": {
                                "code": "ZA",
                                "name": "South Africa",
                                "currency": "ZAR",
                                "flag": "🇿🇦"
                            },
                            "receivingCountries": receiving
                        },
                        "message": f"Successfully retrieved {len(receiving)} destination countries"
                    }
            
            logger.warning("[GET_RECEIVING_COUNTRIES] South Africa (ZA) not found in country list")
            return {
                "success": False,
                "error": "South Africa (ZA) not found in country list",
                "data": None
            }
        
        logger.error(f"[GET_RECEIVING_COUNTRIES] API request failed: {result}")
        return result
    
    @mcp_server.tool()
    async def get_exchange_rate(
        receiving_country: str,
        receiving_currency: str,
        amount: float = 100.0,
        receive: bool = False,
        auto_generate_token: bool = True,
        external_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get exchange rate for sending money from South Africa to destination country.
        
        This tool calculates the exchange rate and fees for remittance transfers.
        It returns multiple product options (e.g., Mobile Money, Cash Pickup) with their respective rates.
        
        Args:
            receiving_country: Destination country code (e.g., "ZW", "KE", "NG", "IN", "PK")
            receiving_currency: Destination currency code (e.g., "USD", "KES", "NGN", "INR", "PKR")
            amount: Amount to send in ZAR (default: 100.0)
            receive: If true, amount is receiving amount; if false, amount is sending amount (default: False)
            auto_generate_token: Auto-generate token if needed (default: True)
            external_token: External authentication token (optional)
        
        Returns:
            dict: Exchange rate details including:
                - rate: Exchange rate
                - fees: Transfer fees
                - amountToPay: Total amount to pay (includes fees)
                - receivingAmount: Amount recipient will receive
                - productName: Delivery method (e.g., "EcoCash", "Cash pickup")
                - productType: Type of product ("wallet", "cash", etc.)
        
        Examples:
            - Zimbabwe (ZW, USD): Mobile money and cash pickup options
            - Kenya (KE, KES): M-Pesa and cash options
            - Nigeria (NG, NGN): Bank transfer and cash options
            - India (IN, INR): Bank transfer options
        """
        logger.info(f"[GET_EXCHANGE_RATE] Tool called: {receiving_country} ({receiving_currency}), amount={amount}, receive={receive}")
        
        # Get token
        token = None
        if external_token:
            token = external_token
            logger.info("[GET_EXCHANGE_RATE] Using external token")
        elif SasaiConfig.USE_TOKEN_MANAGER:
            if auto_generate_token and not token_manager.get_token():
                from auth.tools import generate_authentication_token
                token_result = await generate_authentication_token()
                if not token_result.get("success"):
                    logger.error("[GET_EXCHANGE_RATE] Failed to generate authentication token")
                    raise Exception("Failed to generate authentication token")
            token = token_manager.get_token()
            logger.info("[GET_EXCHANGE_RATE] Using token from manager")
        else:
            logger.error("[GET_EXCHANGE_RATE] Token manager disabled and no external token provided")
            raise Exception("Token manager disabled. Provide external_token.")
        
        # API endpoint
        endpoint = f"{SasaiConfig.BASE_URL}/remittance/v1/product/exchange/rate"
        
        # Request payload
        payload = {
            "sendingCountry": "ZA",
            "receivingCountry": receiving_country,
            "sendingCurrency": "ZAR",
            "receivingCurrency": receiving_currency,
            "amount": amount,
            "receive": receive
        }
        
        logger.info(f"[GET_EXCHANGE_RATE] Getting rate: ZA->'{receiving_country}' ({amount} ZAR)")
        logger.debug(f"[GET_EXCHANGE_RATE] Payload: {payload}")
        
        # Make API request
        client = SasaiAPIClient()
        result = await client.post(
            endpoint=endpoint,
            token=token,
            json_data=payload,
            require_auth=True
        )
        
        # Enhance response
        if result.get('success'):
            items = result.get('data', {}).get('items', [])
            logger.info(f"[GET_EXCHANGE_RATE] Found {len(items)} product options")
            
            # Add request info to result
            result["request_info"] = {
                "sending_country": "ZA",
                "sending_currency": "ZAR",
                "receiving_country": receiving_country,
                "receiving_currency": receiving_currency,
                "amount": amount,
                "receive": receive
            }
            
            # Add helpful message
            if items:
                best_rate = items[0]
                result["message"] = (
                    f"Found {len(items)} delivery option(s) for sending ZAR {amount:.2f} to {receiving_country}. "
                    f"Best rate: 1 ZAR = {float(best_rate.get('rate', 0)):.4f} {receiving_currency} "
                    f"(via {best_rate.get('productName', 'N/A')})"
                )
            else:
                result["message"] = f"No exchange rate options available for {receiving_country} ({receiving_currency})"
        else:
            logger.error(f"[GET_EXCHANGE_RATE] API request failed: {result}")
        
        return result
    
    @mcp_server.tool()
    async def get_recipient_list(
        page: int = 1,
        count: int = 20
    ) -> Dict[str, Any]:
        """
        Get list of saved recipients/beneficiaries for remittance transfers.
        
        Each recipient can have multiple payout methods:
        - Cash Pickup: Physical cash collection
        - Mobile Money: EcoCash, Mukuru, etc.
        - Bank Transfer: Bank account deposits
        
        Args:
            page: Page number for pagination (default: 1)
            count: Number of recipients per page (default: 20, max: 50)
        
        Returns:
            dict: Recipient list with items, total, page, count
        """
        from remittance.recipients import get_recipient_list as fetch_recipients
        return await fetch_recipients(page=page, count=count)
    
    @mcp_server.tool()
    async def generate_remittance_quote(
        recipient_name: str,
        payout_method: str,
        product_id: int,
        amount: str,
        sending_country_id: int = 204,
        receiving_country_id: int = 246,
        sending_currency_id: int = 181,
        receiving_currency_id: int = 153,
        payment_method_id: str = "5",
        receive: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a remittance quote with exchange rate, fees, and total amount breakdown.
        
        This calculates the exact costs for sending money:
        - Exchange rate (ZAR to USD/other currency)
        - Transaction fees
        - VAT/taxes
        - Total amount to pay
        - Amount recipient will receive
        
        Common values:
        - South Africa → Zimbabwe
        - sending_country_id: 204 (South Africa)
        - receiving_country_id: 246 (Zimbabwe)
        - sending_currency_id: 181 (ZAR)
        - receiving_currency_id: 153 (USD)
        - product_id: 629 (EcoCash), 12 (Cash Pickup)
        
        Args:
            recipient_name: Name of the recipient (for display purposes)
            payout_method: Delivery method name (e.g., "EcoCash", "Cash Pickup")
            product_id: Payout product ID (629=EcoCash, 12=Cash Pickup)
            amount: Amount as string (e.g., "100.00")
            sending_country_id: Sending country ID (default: 204 for South Africa)
            receiving_country_id: Receiving country ID (default: 246 for Zimbabwe)
            sending_currency_id: Sending currency ID (default: 181 for ZAR)
            receiving_currency_id: Receiving currency ID (default: 153 for USD)
            payment_method_id: Payment method ID (default: "5")
            receive: If True, amount is recipient amount; if False, sender amount
        
        Returns:
            dict: Quote with calculationId, rates, fees, and amounts
        """
        from remittance.quotes import calculate_remittance_quote
        
        # Add recipient and payout method to the response for UI display
        result = await calculate_remittance_quote(
            sending_country_id=sending_country_id,
            receiving_country_id=receiving_country_id,
            sending_currency_id=sending_currency_id,
            receiving_currency_id=receiving_currency_id,
            amount=amount,
            product_id=product_id,
            payment_method_id=payment_method_id,
            receive=receive
        )
        
        # Enrich response with recipient and payout info for display
        if result and not result.get("error"):
            result["recipientName"] = recipient_name
            result["payoutMethod"] = payout_method
            result["productId"] = product_id
        
        return result
    
    @mcp_server.tool()
    async def execute_remittance_transaction(
        beneficiary_id: str,
        calculation_id: str,
        recipient_name: str,
        payout_method: str,
        sending_amount: str,
        recipient_amount: str,
        payment_method_id: str = "10-I",
        reason_for_transfer: str = "SOWF",
        source_of_funds: str = "SAL"
    ) -> Dict[str, Any]:
        """
        Execute a remittance transaction after user confirms the quote.
        
        This completes the money transfer by processing the payment
        and creating the transaction record.
        
        CRITICAL: beneficiary_id must be from the ACCOUNT that matches the quote's productId.
        
        HOW TO SELECT THE CORRECT ACCOUNT:
        1. From the quote response, get the productId (e.g., 629 for EcoCash)
        2. From the recipient's accounts array, find the account where:
           account.linkedProducts[].productId == quote.productId
        3. Use that account's "id" field as the beneficiary_id
        
        Example from get_recipient_list response:
        {
          "beneficiaryId": "12345",  // <-- DO NOT USE THIS
          "firstName": "John",
          "accounts": [
            {
              "id": "77192529",  // <-- USE THIS if quote.productId = 629
              "beneficiaryPayoutMethod": "EcoCash",
              "linkedProducts": [{"productId": 629, "accountName": "EcoCash"}]
            },
            {
              "id": "77192530",  // <-- USE THIS if quote.productId = 12
              "beneficiaryPayoutMethod": "Cash Pickup",
              "linkedProducts": [{"productId": 12, "accountName": "Cash"}]
            }
          ]
        }
        
        Common codes:
        - Reason for Transfer: "SOWF" (Support of Family), "GIFT" (Gift), "EDUC" (Education)
        - Source of Funds: "SAL" (Salary), "SAV" (Savings), "BUS" (Business)
        - Payment Method: "10-I" (default)
        
        Args:
            beneficiary_id: Account ID where account.linkedProducts[].productId matches quote.productId
            calculation_id: Quote calculation ID (from generate_remittance_quote)
            recipient_name: Recipient's name (for display in receipt)
            payout_method: Payout method name (for display)
            sending_amount: Amount sender is paying (for display)
            recipient_amount: Amount recipient receives (for display)
            payment_method_id: Payment method ID (default: "10-I")
            reason_for_transfer: Reason code (default: "SOWF")
            source_of_funds: Source code (default: "SAL")
        
        Returns:
            dict: Transaction receipt with transactionId, dates, and display info
        """
        from remittance.transactions import execute_remittance_transaction as execute_tx
        
        # Execute the transaction
        result = await execute_tx(
            beneficiary_id=beneficiary_id,
            calculation_id=calculation_id,
            payment_method_id=payment_method_id,
            reason_for_transfer=reason_for_transfer,
            source_of_funds=source_of_funds
        )
        
        # Enrich response with display info for the receipt widget
        if result and not result.get("error"):
            result["recipientName"] = recipient_name
            result["payoutMethod"] = payout_method
            result["sendingAmount"] = sending_amount
            result["recipientAmount"] = recipient_amount
        
        return result
