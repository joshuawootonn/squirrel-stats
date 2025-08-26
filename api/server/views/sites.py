"""
Views for Site CRUD operations.
"""

from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from server.models import Site
from server.serializers import SiteSerializer


class SiteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Site CRUD operations.
    - Users can only see/edit/delete their own sites (by user ID)
    - Automatically assigns the authenticated user's ID as owner
    - Limits users to 50 sites max
    """

    serializer_class = SiteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter sites to only show those owned by the authenticated user.
        Includes page view counts for each site.
        """
        # Get the user_id from the request (set by ClerkAuthentication)
        if hasattr(self.request, "user_id"):
            return Site.objects.filter(user_id=self.request.user_id).annotate(pageview_count=Count("page_views"))
        return Site.objects.none()

    def perform_create(self, serializer):
        """
        Set the user_id to the authenticated user when creating a site.
        """
        if hasattr(self.request, "user_id"):
            serializer.save(user_id=self.request.user_id)
        else:
            raise ValueError("No authenticated user found")

    def create(self, request, *args, **kwargs):
        """
        Create a new site with validation for site limit.
        """
        # Check site limit
        if hasattr(request, "user_id"):
            site_count = Site.objects.filter(user_id=request.user_id).count()
            if site_count >= 50:
                return Response(
                    {"error": "Site limit reached. Maximum 50 sites allowed."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return super().create(request, *args, **kwargs)
