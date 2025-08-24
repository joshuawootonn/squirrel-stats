"""
Simple Clerk authentication for Django REST Framework.
"""

import logging

from clerk_backend_api import AuthenticateRequestOptions
from django.conf import settings
from rest_framework import authentication, exceptions

logger = logging.getLogger(__name__)


class ClerkUser:
    """
    Simple user object that holds user ID from Clerk.
    Provides compatibility with DRF's authentication system.
    """

    def __init__(self, user_id):
        self.user_id = user_id
        self.id = user_id  # For compatibility
        self.pk = user_id  # For DRF throttling compatibility

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False


class ClerkAuthentication(authentication.BaseAuthentication):
    """
    Simple authentication class for Clerk session tokens.

    Only verifies tokens and extracts user_id - no user sync needed.

    Expects the Authorization header in format:
    Authorization: Bearer <session_token>
    """

    def authenticate(self, request):
        """
        Authenticate the request using Clerk session token with modern networkless verification.

        Returns:
            tuple: (user, token) if authenticated, None otherwise
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
            auth_options = AuthenticateRequestOptions()

            request_state = clerk.authenticate_request(request, auth_options)

            if not request_state.is_signed_in:
                raise exceptions.AuthenticationFailed("Invalid session")

            # Extract user ID from the JWT payload
            if not request_state.payload:
                raise exceptions.AuthenticationFailed("No payload found in token")

            user_id = request_state.payload.get("sub")  # 'sub' (subject) contains the user ID in JWT

            if not user_id:
                raise exceptions.AuthenticationFailed("No user ID found in token")

            user = ClerkUser(user_id)

            request.user_id = user_id

            logger.debug(f"Successfully authenticated user: {user_id}")
            return (user, token)

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise exceptions.AuthenticationFailed("Invalid authentication token")

    def authenticate_header(self, request):
        """
        Return the WWW-Authenticate header.
        """
        return 'Bearer realm="api"'
