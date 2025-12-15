"""
Context variables for request-scoped data.
This module is separate to avoid circular imports.
"""

from contextvars import ContextVar
from typing import Optional

# Context variable to store Sasai token for LangGraph nodes
# This is set by middleware and accessed by LangGraph nodes
sasai_token_context: ContextVar[Optional[str]] = ContextVar('sasai_token', default=None)

# Context variable to store the user's language preference
language_context: ContextVar[str] = ContextVar('language', default='en')

