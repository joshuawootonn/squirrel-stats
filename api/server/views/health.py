from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple health check endpoint to verify DRF is working.
    """
    # Check if Clerk is configured
    clerk_configured = bool(settings.CLERK_SECRET_KEY and settings.CLERK_CLIENT)

    return Response(
        {
            "status": "healthy",
            "message": "Django REST Framework is configured and working!",
            "version": "v1",
            "clerk_configured": clerk_configured,
        },
        status=status.HTTP_200_OK,
    )
