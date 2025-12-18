"""HTTP client for Sasai Payment Gateway API."""

import httpx
import logging
from typing import Dict, Any, Optional

from config.settings import SasaiConfig
from core.exceptions import (
    SasaiAPIError,
    AuthenticationError,
    TokenExpiredError,
    APITimeoutError,
    NetworkError,
    ValidationError,
    RateLimitError,
    ServerError
)

logger = logging.getLogger(__name__)


class SasaiAPIClient:
    """HTTP client wrapper for Sasai Payment Gateway API calls."""
    
    def __init__(self):
        """Initialize the API client."""
        self._timeout = httpx.Timeout(SasaiConfig.REQUEST_TIMEOUT)
    
    async def make_authenticated_request(
        self,
        method: str,
        endpoint: str,
        token: Optional[str] = None,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        require_auth: bool = True,
        timeout: Optional[float] = None
    ) -> Dict[Any, Any]:
        """
        Make an authenticated HTTP request to the Sasai Payment Gateway.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint URL
            token: Authentication token
            params: Query parameters
            json_data: JSON payload for POST requests
            require_auth: Whether authentication token is required
            timeout: Request timeout in seconds (overrides default)
            
        Returns:
            dict: API response data
            
        Raises:
            AuthenticationError: If authentication is required but token is missing
            TokenExpiredError: If the authentication token has expired
            ValidationError: If request validation fails
            APITimeoutError: If the request times out
            NetworkError: If network connectivity issues occur
            RateLimitError: If API rate limits are exceeded
            ServerError: If the server returns a server error
            SasaiAPIError: For other API-related errors
        """
        # Check authentication requirement
        if require_auth and not token:
            raise AuthenticationError("Authentication token required. Please call generate_token first.")
        
        # Prepare headers
        headers = SasaiConfig.DEFAULT_HEADERS.copy()
        if token and require_auth:
            headers["Authorization"] = f"Bearer {token}"
        
        # Log API call details
        import sys
        token_preview = token[:20] + "..." if token else "None"
        print(f"[API_CLIENT] {method.upper()} {endpoint}", flush=True)
        print(f"[API_CLIENT] Headers: {dict((k, v if k != 'Authorization' else f'Bearer {token_preview}') for k, v in headers.items())}", flush=True)
        if params:
            print(f"[API_CLIENT] Query params: {params}", flush=True)
        if json_data:
            # Hide sensitive data in JSON payload
            safe_json = json_data.copy()
            if 'pin' in safe_json:
                safe_json['pin'] = '***HIDDEN***'
            print(f"[API_CLIENT] JSON payload: {safe_json}", flush=True)
        
        # Use custom timeout if provided
        request_timeout = httpx.Timeout(timeout) if timeout else self._timeout
        
        try:
            async with httpx.AsyncClient(timeout=request_timeout) as client:
                # Make the appropriate HTTP request
                if method.upper() == "GET":
                    response = await client.get(endpoint, params=params, headers=headers)
                    print(f"[API_CLIENT] GET response status: {response.status_code}", flush=True)
                    print(f"[API_CLIENT] GET response URL: {response.url}", flush=True)
                elif method.upper() == "POST":
                    response = await client.post(endpoint, params=params, json=json_data, headers=headers)
                    print(f"[API_CLIENT] POST response status: {response.status_code}", flush=True)
                    print(f"[API_CLIENT] POST response URL: {response.url}", flush=True)
                elif method.upper() == "PUT":
                    response = await client.put(endpoint, params=params, json=json_data, headers=headers)
                    print(f"[API_CLIENT] PUT response status: {response.status_code}")
                elif method.upper() == "DELETE":
                    response = await client.delete(endpoint, params=params, headers=headers)
                    print(f"[API_CLIENT] DELETE response status: {response.status_code}")
                elif method.upper() == "PATCH":
                    response = await client.patch(endpoint, params=params, json=json_data, headers=headers)
                    print(f"[API_CLIENT] PATCH response status: {response.status_code}")
                else:
                    raise ValidationError(f"Unsupported HTTP method: {method}")
                
                # Log response details
                import sys
                print(f"[API_CLIENT] Response status: {response.status_code}", flush=True)
                # print(f"[API_CLIENT] Response headers: {dict(response.headers)}", flush=True)
                try:
                    response_preview = response.text[:200] if response.text else "Empty response"
                    print(f"[API_CLIENT] Response preview: {response_preview}", flush=True)
                except:
                    print(f"[API_CLIENT] Could not read response text", flush=True)
                
                return self._handle_response(response, endpoint)
                    
        except httpx.TimeoutException:
            timeout_value = timeout or SasaiConfig.REQUEST_TIMEOUT
            raise APITimeoutError(
                f"Request timeout: API did not respond within {timeout_value} seconds",
                timeout=timeout_value,
                endpoint=endpoint
            )
        except httpx.NetworkError as e:
            raise NetworkError(
                f"Network error: Unable to connect to payment gateway - {str(e)}",
                endpoint=endpoint
            )
        except Exception as e:
            # Re-raise our custom exceptions
            if isinstance(e, SasaiAPIError):
                raise
            # Wrap unexpected errors
            raise SasaiAPIError(f"Unexpected error during API request: {str(e)}", endpoint=endpoint)
    
    def _handle_response(self, response: httpx.Response, endpoint: str) -> Dict[Any, Any]:
        """
        Handle HTTP response and convert to appropriate exceptions.
        
        Args:
            response: HTTP response object
            endpoint: API endpoint that was called
            
        Returns:
            dict: Processed response data
            
        Raises:
            Various SasaiAPIError subclasses based on response status
        """
        # Success response - handle all 2xx status codes
        if 200 <= response.status_code < 300:
            # Handle empty body responses (e.g., 204 No Content)
            if not response.text.strip():
                response_data = None
            else:
                try:
                    response_data = response.json()
                except (ValueError, Exception):
                    # Fallback for non-JSON responses
                    response_data = {"message": response.text}
            
            return {
                "success": True,
                "data": response_data,
                "status_code": response.status_code,
                "endpoint": str(response.url)
            }
        
        # Handle different error status codes
        elif response.status_code == 401:
            raise TokenExpiredError(
                "Authentication failed. Token may be expired. Please call generate_token again.",
                status_code=response.status_code,
                endpoint=endpoint
            )
        
        elif response.status_code == 400:
            try:
                error_data = response.json()
                error_message = error_data.get("message", "Bad request")
                field = error_data.get("field")
            except:
                error_message = response.text or "Bad request"
                field = None
            
            raise ValidationError(
                f"Bad request: {error_message}",
                status_code=response.status_code,
                endpoint=endpoint,
                field=field
            )
        
        elif response.status_code == 404:
            raise SasaiAPIError(
                f"API endpoint not found: {endpoint}",
                status_code=response.status_code,
                endpoint=endpoint
            )
        
        elif response.status_code == 429:
            # Extract retry-after header if available
            retry_after = None
            if "retry-after" in response.headers:
                try:
                    retry_after = int(response.headers["retry-after"])
                except ValueError:
                    pass
            
            raise RateLimitError(
                "Rate limit exceeded. Please wait before making more requests.",
                status_code=response.status_code,
                endpoint=endpoint,
                retry_after=retry_after
            )
        
        elif response.status_code >= 500:
            raise ServerError(
                f"Server error: Payment gateway is experiencing issues (Status: {response.status_code})",
                status_code=response.status_code,
                endpoint=endpoint
            )
        
        else:
            # Handle other error codes
            try:
                error_data = response.json()
                error_message = error_data.get("message", f"HTTP {response.status_code}")
            except:
                error_message = f"HTTP {response.status_code}"
            
            raise SasaiAPIError(
                f"API request failed: {error_message}",
                status_code=response.status_code,
                endpoint=endpoint
            )
    
    async def get(self, endpoint: str, token: Optional[str] = None, **kwargs) -> Dict[Any, Any]:
        """Make a GET request."""
        return await self.make_authenticated_request("GET", endpoint, token=token, **kwargs)
    
    async def post(self, endpoint: str, token: Optional[str] = None, **kwargs) -> Dict[Any, Any]:
        """Make a POST request."""
        return await self.make_authenticated_request("POST", endpoint, token=token, **kwargs)
    
    async def put(self, endpoint: str, token: Optional[str] = None, **kwargs) -> Dict[Any, Any]:
        """Make a PUT request."""
        return await self.make_authenticated_request("PUT", endpoint, token=token, **kwargs)
    
    async def delete(self, endpoint: str, token: Optional[str] = None, **kwargs) -> Dict[Any, Any]:
        """Make a DELETE request."""
        return await self.make_authenticated_request("DELETE", endpoint, token=token, **kwargs)
    
    async def patch(self, endpoint: str, token: Optional[str] = None, **kwargs) -> Dict[Any, Any]:
        """Make a PATCH request."""
        return await self.make_authenticated_request("PATCH", endpoint, token=token, **kwargs)
    
    async def get_recipient_list(self, token: str, page: int = 1, count: int = 20) -> Dict[Any, Any]:
        """
        Fetch list of saved recipients/beneficiaries.
        
        Args:
            token: Authentication bearer token
            page: Page number for pagination (default: 1)
            count: Number of items per page (default: 20, max: 50)
            
        Returns:
            dict: Response with items, total, page, count
        """
        endpoint = f"{SasaiConfig.BASE_URL}/remittance/v1/recipient/list"
        params = {
            "page": page,
            "count": min(count, 50)  # Limit to max 50
        }
        
        logger.info(f"[API_CLIENT] Fetching recipients from {endpoint} with params {params}")
        result = await self.get(endpoint, token=token, params=params)
        logger.info(f"[API_CLIENT] Recipient API result: success={result.get('success')}, data keys={list(result.get('data', {}).keys())}")
        
        if result.get("success"):
            data = result.get("data", {})
            logger.info(f"[API_CLIENT] Items in response: {len(data.get('items', []))}")
            return data
        else:
            logger.warning(f"[API_CLIENT] Recipient API failed: {result}")
            return {
                "items": [],
                "total": 0,
                "page": page,
                "count": count,
                "error": "Failed to fetch recipients"
            }
    
    async def calculate_rate(self, token: str, payload: Dict[Any, Any]) -> Dict[Any, Any]:
        """
        Calculate remittance quote with exchange rate, fees, and total amount.
        
        Args:
            token: Authentication bearer token
            payload: Request payload containing:
                - sendingCountryId: ID of sending country (e.g., 204 for South Africa)
                - receivingCountryId: ID of receiving country (e.g., 246 for Zimbabwe)
                - sendingCurrencyId: ID of sending currency (e.g., 181 for ZAR)
                - receivingCurrencyId: ID of receiving currency (e.g., 153 for USD)
                - amount: Amount as string (e.g., "100.00")
                - productId: Payout product ID (629=EcoCash, 12=Cash Pickup)
                - receive: Boolean - if true, amount is recipient amount
                - paymentMethodId: Payment method ID (usually "5")
                - spgOrderId: Optional order ID
                - notes: Optional notes dict
                
        Returns:
            dict: Quote details with calculationId, rates, fees, amounts
        """
        endpoint = f"{SasaiConfig.BASE_URL}/remittance/v1/rate/calculation"
        
        logger.info(f"[API_CLIENT] Calculating rate at {endpoint}")
        logger.info(f"[API_CLIENT] Payload: amount={payload.get('amount')}, productId={payload.get('productId')}")
        
        result = await self.post(endpoint, token=token, json_data=payload)
        logger.info(f"[API_CLIENT] Rate calculation result: success={result.get('success')}")
        
        if result.get("success"):
            data = result.get("data", {})
            logger.info(f"[API_CLIENT] Quote - Sending: {data.get('sendingAmount')}, Receiving: {data.get('recipientAmount')}, Rate: {data.get('rate')}, Fees: {data.get('fees')}, Total: {data.get('amountToPay')}")
            return data
        else:
            logger.warning(f"[API_CLIENT] Rate calculation failed: {result}")
            return {
                "success": False,
                "error": result.get("error", "Failed to calculate rate")
            }
    
    async def execute_transaction(self, token: str, payload: Dict[Any, Any]) -> Dict[Any, Any]:
        """
        Execute a remittance transaction after quote confirmation.
        
        Args:
            token: Authentication bearer token
            payload: Request payload containing:
                - reasonForTransfer: Reason code (e.g., "SOWF" - Support of Family)
                - sourceOfFunds: Source code (e.g., "SAL" - Salary)
                - beneficiaryId: Recipient/beneficiary ID
                - calculationId: Quote calculation ID from previous step
                - paymentMethodId: Payment method ID (e.g., "10-I")
                
        Returns:
            dict: Transaction details with:
                - transactionId: Unique transaction ID
                - transactionDate: When transaction was created
                - expiryDate: When transaction expires
                - promocode: Applied promo code (if any)
        """
        endpoint = f"{SasaiConfig.BASE_URL}/remittance/v1/transaction"
        
        logger.info(f"[API_CLIENT] Executing transaction at {endpoint}")
        logger.info(f"[API_CLIENT] Payload: beneficiaryId={payload.get('beneficiaryId')}, calculationId={payload.get('calculationId')}")
        
        result = await self.post(endpoint, token=token, json_data=payload)
        logger.info(f"[API_CLIENT] Transaction result: success={result.get('success')}")
        
        if result.get("success"):
            data = result.get("data", {})
            logger.info(f"[API_CLIENT] Transaction - ID: {data.get('transactionId')}, Date: {data.get('transactionDate')}")
            return data
        else:
            logger.warning(f"[API_CLIENT] Transaction execution failed: {result}")
            return {
                "success": False,
                "error": result.get("error", "Failed to execute transaction")
            }

