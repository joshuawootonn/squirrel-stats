"""
Clerk authentication utilities for Django.
"""

import logging
from typing import Optional

from clerk_backend_api import Clerk
from clerk_backend_api.models import Session, User
from django.conf import settings

logger = logging.getLogger(__name__)


def get_clerk_client() -> Optional[Clerk]:
    """
    Get the Clerk client instance from settings.

    Returns:
        Clerk client instance or None if not configured
    """
    return getattr(settings, "CLERK_CLIENT", None)


def verify_session_token(session_token: str) -> Optional[Session]:
    """
    Verify a Clerk session token.

    Args:
        session_token: The session token to verify

    Returns:
        Session object if valid, None otherwise
    """
    clerk = get_clerk_client()
    if not clerk:
        logger.error("Clerk client not configured")
        return None

    try:
        # Verify the session token
        session = clerk.sessions.verify_token(
            token=session_token,
            session_token=session_token,
        )
        return session
    except Exception as e:
        logger.error(f"Failed to verify session token: {e}")
        return None


def get_user_from_session(session: Session) -> Optional[User]:
    """
    Get user details from a verified session.

    Args:
        session: Verified Clerk session

    Returns:
        User object if found, None otherwise
    """
    clerk = get_clerk_client()
    if not clerk or not session:
        return None

    try:
        # Get user details
        user = clerk.users.get(user_id=session.user_id)
        return user
    except Exception as e:
        logger.error(f"Failed to get user from session: {e}")
        return None


def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Get user details by Clerk user ID.

    Args:
        user_id: Clerk user ID

    Returns:
        User object if found, None otherwise
    """
    clerk = get_clerk_client()
    if not clerk:
        return None

    try:
        user = clerk.users.get(user_id=user_id)
        return user
    except Exception as e:
        logger.error(f"Failed to get user by ID: {e}")
        return None
