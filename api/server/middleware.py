"""
Middleware for handling Kamal-specific issues.
"""

import re

from django.conf import settings
from django.http import JsonResponse


class KamalHealthCheckMiddleware:
    """
    Middleware to handle Kamal health check requests that use container IDs in Host headers.

    This addresses the issue described in: https://github.com/basecamp/kamal/issues/992

    Kamal-proxy uses the container ID in the Host header for health checks, but Django's
    ALLOWED_HOSTS validation rejects it. This middleware intercepts health check requests
    and handles them before ALLOWED_HOSTS validation occurs.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if this is a health check request with a container ID host
        if self._is_kamal_health_check(request):
            return self._handle_health_check()

        return self.get_response(request)

    def _is_kamal_health_check(self, request):
        """Check if this is a Kamal health check request."""
        # Must be a GET request to /up endpoint
        if request.method != "GET" or request.path != "/up":
            return False

        # Check if the host looks like a Docker container ID (12 hex chars)
        # Use META to avoid triggering ALLOWED_HOSTS validation
        host = request.META.get("HTTP_HOST", "")
        if ":" in host:
            host = host.split(":")[0]  # Remove port

        # Docker container IDs are 12 hex characters
        return bool(re.match(r"^[a-f0-9]{12}$", host))

    def _handle_health_check(self):
        """Return a health check response."""
        # Check if Clerk is configured (same logic as the original health check)
        clerk_configured = bool(getattr(settings, "CLERK_SECRET_KEY", None) and getattr(settings, "CLERK_CLIENT", None))

        return JsonResponse(
            {
                "status": "healthy",
                "message": "Django REST Framework is configured and working!",
                "version": "v1",
                "clerk_configured": clerk_configured,
            }
        )
