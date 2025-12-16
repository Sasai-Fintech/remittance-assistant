"""Token management for Sasai Payment Gateway authentication."""

from typing import Optional, Dict, Any
from config.settings import SasaiConfig


class TokenManager:
    """Manages authentication tokens for the Sasai Payment Gateway."""
    
    def __init__(self):
        """Initialize the token manager."""
        self._current_token: Optional[str] = None
        self._token_metadata: Dict[str, Any] = {}
        self._enabled = SasaiConfig.USE_TOKEN_MANAGER
    
    def set_token(self, token: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Set the current authentication token.
        
        Args:
            token: The authentication token
            metadata: Optional metadata about the token (e.g., expiry, source)
        """
        if not self._enabled:
            return  # Ignore if token manager is disabled
        self._current_token = token
        self._token_metadata = metadata or {}
    
    def get_token(self, external_token: Optional[str] = None) -> Optional[str]:
        """
        Get the current authentication token.
        
        Args:
            external_token: Optional external token to use instead of managed token
        
        Returns:
            str or None: Current authentication token if available
        """
        # If external token is provided, use it (regardless of token manager state)
        if external_token:
            return external_token
        
        # If token manager is disabled, return None (must use external tokens)
        if not self._enabled:
            return None
        
        return self._current_token
    
    def get_token_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the current token.
        
        Returns:
            dict: Token metadata
        """
        return self._token_metadata.copy()
    
    def has_token(self, external_token: Optional[str] = None) -> bool:
        """
        Check if a token is currently available.
        
        Args:
            external_token: Optional external token to check
        
        Returns:
            bool: True if token is available, False otherwise
        """
        # If external token is provided, it's available
        if external_token:
            return True
        
        # If token manager is disabled, only external tokens are available
        if not self._enabled:
            return False
        
        return self._current_token is not None
    
    def clear_token(self) -> bool:
        """
        Clear the current authentication token.
        
        Returns:
            bool: True if a token was cleared, False if no token was present
        """
        if not self._enabled:
            return False
        had_token = self._current_token is not None
        self._current_token = None
        self._token_metadata = {}
        return had_token
    
    def get_token_status(self) -> Dict[str, Any]:
        """
        Get comprehensive token status information.
        
        Returns:
            dict: Token status information
        """
        return {
            "token_manager_enabled": self._enabled,
            "token_available": self.has_token(),
            "token_preview": self._current_token[:20] + "..." if self._current_token else None,
            "token_length": len(self._current_token) if self._current_token else 0,
            "metadata": self._token_metadata.copy(),
            "recommendation": "Token is available" if self.has_token() else (
                "Token manager is disabled. Pass external_token parameter to tools." if not self._enabled
                else "Call generate_token to authenticate"
            )
        }
    
    def is_enabled(self) -> bool:
        """
        Check if token manager is enabled.
        
        Returns:
            bool: True if token manager is enabled, False otherwise
        """
        return self._enabled


# Global token manager instance
token_manager = TokenManager()
