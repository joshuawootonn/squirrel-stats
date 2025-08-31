"""
Custom authentication classes for the API.
"""

from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Session authentication without CSRF validation for API endpoints.

    This is safe for API endpoints when using CORS properly configured
    and when the frontend is a separate domain/port.
    """

    def enforce_csrf(self, request):
        return  # Skip CSRF validation
