"""
JWT Authentication utilities for EcoCash Assistant backend.

This module provides utilities for extracting and handling JWT tokens
from incoming requests. For MVP, we simply extract and forward tokens
without validation (trusting the mobile shell). Production should add
JWKS validation and expiry enforcement.
"""

from typing import Optional
from fastapi import Header, Request


async def get_jwt_token(
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> Optional[str]:
    """
    Extract JWT token from Authorization header.
    
    Args:
        authorization: Authorization header value (e.g., "Bearer <token>")
        
    Returns:
        JWT token string if present, None otherwise
    """
    if not authorization:
        return None
    
    # Handle "Bearer <token>" format
    if authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "").strip()
        if token:
            return token
    
    return None


async def get_user_id(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id")
) -> Optional[str]:
    """
    Extract user ID from X-User-Id header.
    
    Args:
        x_user_id: X-User-Id header value
        
    Returns:
        User ID string if present, None otherwise
    """
    return x_user_id if x_user_id else None


def extract_jwt_from_request(request: Request) -> Optional[str]:
    """
    Extract JWT token from FastAPI request object.
    
    This is a convenience function for extracting JWT from request headers
    when not using FastAPI dependencies.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        JWT token string if present, None otherwise
    """
    authorization = request.headers.get("Authorization") or request.headers.get("authorization")
    if authorization and authorization.startswith("Bearer "):
        return authorization.replace("Bearer ", "").strip()
    return None


def extract_user_id_from_request(request: Request) -> Optional[str]:
    """
    Extract user ID from FastAPI request object.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        User ID string if present, None otherwise
    """
    return request.headers.get("X-User-Id") or request.headers.get("x-user-id")


def extract_sasai_token_from_request(request: Request) -> Optional[str]:
    """
    Extract Sasai authentication token from FastAPI request object.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Sasai token string if present, None otherwise
    """
    return request.headers.get("X-Sasai-Token") or request.headers.get("x-sasai-token")

