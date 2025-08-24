"""
Authentication-related views.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    Get the current authenticated user's account information.
    """
    if hasattr(request, "account"):
        account = request.account
        return Response(
            {
                "id": str(account.id),
                "clerk_user_id": account.clerk_user_id,
                "email": account.email,
                "first_name": account.first_name,
                "last_name": account.last_name,
                "created_at": account.created_at,
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response({"error": "No account found"}, status=status.HTTP_404_NOT_FOUND)
