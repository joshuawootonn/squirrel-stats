from django.urls import path

from .views.general import index
from .views.health import health_check
from .views.pageviews import track_pageview

urlpatterns = [
    path("", index, name="index"),
    path("pv", track_pageview, name="track_pageview"),
    path("health/", health_check, name="health_check"),
]
