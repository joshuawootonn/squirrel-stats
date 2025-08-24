"""
Simple Clerk authentication for Django REST Framework.
"""

import logging

from django.conf import settings
from rest_framework import authentication, exceptions

from .clerk import sync_user_from_clerk

logger = logging.getLogger(__name__)


class ClerkAuthentication(authentication.BaseAuthentication):
    """
    Simple authentication class for Clerk session tokens.

    Expects the Authorization header in format:
    Authorization: Bearer <session_token>
    """

    def authenticate(self, request):
        """
        Authenticate the request using Clerk session token.

        Returns:
            tuple: (account, token) if authenticated, None otherwise
        """
        # Get the authorization header
        auth_header = authentication.get_authorization_header(request).decode("utf-8")

        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        # Extract the token
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return None

        # Get Clerk client
        clerk = settings.CLERK_CLIENT
        if not clerk:
            logger.error("Clerk client not configured")
            raise exceptions.AuthenticationFailed("Authentication service unavailable")

        try:
            # Verify the session token with Clerk
            session = clerk.sessions.verify(
                session_id=token,
                token=token,
            )

            if not session or not session.user_id:
                raise exceptions.AuthenticationFailed("Invalid session")

            # Sync or get the user account
            account = sync_user_from_clerk(session.user_id)
            if not account:
                raise exceptions.AuthenticationFailed("Failed to sync user account")

            # Attach the account to the request
            request.account = account

            return (account, token)

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise exceptions.AuthenticationFailed("Invalid authentication token")

    def authenticate_header(self, request):
        """
        Return the WWW-Authenticate header.
        """
        return 'Bearer realm="api"'
