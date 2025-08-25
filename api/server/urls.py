from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views.general import index
from .views.health import health_check
from .views.pageviews import track_pageview
from .views.sites import SiteViewSet

# Create a router for ViewSets
router = DefaultRouter()
router.register(r"sites", SiteViewSet, basename="site")

urlpatterns = [
    path("", index, name="index"),
    path("pv", track_pageview, name="track_pageview"),
    path("up", health_check, name="health_check"),
    # Include the router URLs
    path("", include(router.urls)),
]
