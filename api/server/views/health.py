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
    return Response(
        {
            "status": "healthy",
            "message": "Django REST Framework is configured and working!",
            "version": "v1",
        },
        status=status.HTTP_200_OK,
    )
