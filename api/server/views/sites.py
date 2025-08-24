"""
Views for Site CRUD operations.
"""

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from server.models import Site
from server.serializers import SiteSerializer


class SiteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Site CRUD operations.
    - Users can only see/edit/delete their own sites
    - Automatically assigns the authenticated user as owner
    - Limits users to 50 sites max
    """

    serializer_class = SiteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter sites to only show those owned by the authenticated user.
        """
        # Get the account from the request (set by ClerkAuthentication)
        if hasattr(self.request, "account"):
            return Site.objects.filter(owner=self.request.account)
        return Site.objects.none()

    def perform_create(self, serializer):
        """
        Set the owner to the authenticated user when creating a site.
        """
        if hasattr(self.request, "account"):
            serializer.save(owner=self.request.account)
        else:
            raise ValueError("No authenticated account found")

    def create(self, request, *args, **kwargs):
        """
        Create a new site with validation for site limit.
        """
        # Check site limit
        if hasattr(request, "account"):
            site_count = Site.objects.filter(owner=request.account).count()
            if site_count >= 50:
                return Response(
                    {"error": "Site limit reached. Maximum 50 sites allowed."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return super().create(request, *args, **kwargs)
