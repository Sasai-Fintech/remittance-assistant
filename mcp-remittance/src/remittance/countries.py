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
    async def calculate_rate_and_lock(
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
        Lock in exchange rate for selected vendor and generate calculationId.
        
        This is Step 2 in the remittance flow: After user selects a delivery method
        (e.g., EcoCash, Cash Pickup) from the exchange rate options, this function
        locks in that rate and generates a calculationId.
        
        The calculationId will be used in the next step to generate the actual quote.
        
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
            dict: Rate calculation with calculationId, rates, fees, and amounts
        """
        from remittance.quotes import calculate_remittance_quote
        
        # Call Step 2: Lock rate and get calculationId
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
    async def generate_remittance_quote(
        beneficiary_id: str,
        calculation_id: str,
        recipient_name: str,
        payout_method: str,
        # All rate calculation fields to pass through to widget
        sending_amount: str,
        recipient_amount: str,
        rate: str,
        fees: str,
        vat: str,
        amount_to_pay: str,
        reverse_rate: Optional[str] = None,
        surcharges: Optional[str] = "0.00",
        # Transaction parameters
        payment_method_id: str = "10-I",
        reason_for_transfer: str = "SOWF",
        source_of_funds: str = "SAL"
    ) -> Dict[str, Any]:
        """
        Generate quote using calculationId from rate calculation.
        
        This is Step 3 in the remittance flow: Uses the calculationId from Step 2
        to generate a quote and returns a transactionId.
        
        CRITICAL: This tool creates the actual quote on the backend and returns
        a transactionId. All rate calculation data (from Step 2) must be passed
        through to this tool so it can be displayed in the QuoteCard widget.
        
        beneficiary_id MUST be from the ACCOUNT that matches the product!
        
        HOW TO SELECT THE CORRECT ACCOUNT:
        1. From the rate calculation response, get the productId
        2. From the recipient's accounts array, find the account where:
           account.linkedProducts[].productId == productId
        3. Use that account's "id" field as the beneficiary_id
        
        Example from get_recipient_list response:
        {
          "beneficiaryId": "12345",  // <-- DO NOT USE THIS
          "firstName": "John",
          "accounts": [
            {
              "id": "77192529",  // <-- USE THIS if productId = 629
              "beneficiaryPayoutMethod": "EcoCash",
              "linkedProducts": [{"productId": 629, "accountName": "EcoCash"}]
            },
            {
              "id": "77192530",  // <-- USE THIS if productId = 12
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
            beneficiary_id: Account ID where account.linkedProducts[].productId matches productId
            calculation_id: Calculation ID from calculate_rate_and_lock (Step 2)
            recipient_name: Recipient's name (for display in quote)
            payout_method: Payout method name (for display)
            sending_amount: Amount sender is paying (from Step 2)
            recipient_amount: Amount recipient receives (from Step 2)
            rate: Exchange rate (from Step 2)
            fees: Transaction fees (from Step 2)
            vat: VAT amount (from Step 2)
            amount_to_pay: Total amount to pay (from Step 2)
            reverse_rate: Reverse exchange rate (optional, from Step 2)
            surcharges: Surcharges (optional, from Step 2)
            payment_method_id: Payment method ID (default: "10-I")
            reason_for_transfer: Reason code (default: "SOWF")
            source_of_funds: Source code (default: "SAL")
        
        Returns:
            dict: Quote with transactionId AND all rate calculation data for display
        """
        from remittance.quotes import generate_remittance_quote_from_calculation
        
        # Call Step 3: Generate quote and get transactionId
        result = await generate_remittance_quote_from_calculation(
            beneficiary_id=beneficiary_id,
            calculation_id=calculation_id,
            payment_method_id=payment_method_id,
            reason_for_transfer=reason_for_transfer,
            source_of_funds=source_of_funds
        )
        
        # Enrich response with ALL rate calculation data AND display info for the quote widget
        if result and not result.get("error"):
            result["recipientName"] = recipient_name
            result["payoutMethod"] = payout_method
            result["calculationId"] = calculation_id  # Keep for reference
            # Pass through all rate calculation data from Step 2
            result["sendingAmount"] = sending_amount
            result["recipientAmount"] = recipient_amount
            result["rate"] = rate
            result["fees"] = fees
            result["vat"] = vat
            result["amountToPay"] = amount_to_pay
            if reverse_rate:
                result["reverseRate"] = reverse_rate
            if surcharges:
                result["surcharges"] = surcharges
        
        return result
    
    @mcp_server.tool()
    async def get_payment_options(
        service_type: str = "ZAPersonPaymentOptions"
    ) -> Dict[str, Any]:
        """
        Get available payment options for completing the transaction.
        
        This is Step 4a in the remittance flow: After user confirms the quote,
        show them the available payment methods (e.g., Bank Transfer, Card, Wallet)
        so they can select how to pay.
        
        Call this BEFORE execute_remittance_transaction.
        
        Args:
            service_type: Service type for payment options (default: "ZAPersonPaymentOptions")
        
        Returns:
            dict: Payment options list with code, name, description, and icon for each method
            
        Example Response:
            {
                "paymentOptions": [
                    {
                        "code": "EFT",
                        "name": "Electronic Funds Transfer",
                        "description": "Bank transfer from your account"
                    },
                    {
                        "code": "CARD",
                        "name": "Debit/Credit Card",
                        "description": "Pay with your card"
                    }
                ]
            }
        """
        from remittance.payments import get_payment_options as fetch_payment_options
        return await fetch_payment_options(service_type=service_type)
    
    @mcp_server.tool()
    async def execute_remittance_transaction(
        transaction_id: str,
        payment_method_code: str,
        recipient_name: str,
        payout_method: str,
        sending_amount: str,
        recipient_amount: str
    ) -> Dict[str, Any]:
        """
        Complete/execute transaction using transactionId from quote and payment method code.
        
        This is Step 4 in the remittance flow: Uses PATCH to finalize the transaction
        with ONLY the transactionId (from Step 3) and paymentMethodCode (from Step 4a).
        
        IMPORTANT: The PATCH /v1/transaction endpoint requires ONLY:
        - transactionId from Step 3
        - paymentMethodCode from Step 4a (user selected payment method)
        
        CRITICAL: payment_method_code MUST be from the payment options widget!
        - User MUST select a payment method from Step 4a (get_payment_options)
        - Extract the 'code' field from the selected payment option
        - Examples: "eft", "cash", "card"
        
        Args:
            transaction_id: Transaction ID from generate_remittance_quote (Step 3)
            payment_method_code: Payment method CODE from user selection in Step 4a (e.g., "eft", "card", "cash")
            recipient_name: Recipient's name (for display in receipt)
            payout_method: Payout method name (for display)
            sending_amount: Amount sender paid (for display)
            recipient_amount: Amount recipient receives (for display)
        
        Returns:
            dict: Final transaction receipt with confirmation and display info
        """
        from remittance.transactions import execute_remittance_transaction as execute_tx
        
        # Call Step 4: Complete the transaction with ONLY transactionId and paymentMethodCode
        result = await execute_tx(
            transaction_id=transaction_id,
            payment_method_code=payment_method_code
        )
        
        # Enrich response with display info for the receipt widget
        if result and not result.get("error"):
            result["recipientName"] = recipient_name
            result["payoutMethod"] = payout_method
            result["sendingAmount"] = sending_amount
            result["recipientAmount"] = recipient_amount
            result["transactionId"] = transaction_id  # Ensure it's in response
            result["paymentMethodCode"] = payment_method_code  # Keep for reference
            
            # Highlight transactionUrl if present
            transaction_url = result.get("transactionUrl")
            if transaction_url:
                result["actionRequired"] = True
                result["actionUrl"] = transaction_url
                result["actionMessage"] = "Please complete your payment by opening this URL"
        
        return result
