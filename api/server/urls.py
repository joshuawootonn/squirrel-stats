from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views.auth import (
    forgot_password_view,
    login_view,
    logout_view,
    reset_password_view,
    signup_view,
    user_info_view,
)
from .views.chart import chart_data
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
    path("chart", chart_data, name="chart_data"),
    # Authentication endpoints
    path("auth/signup", signup_view, name="signup"),
    path("auth/login", login_view, name="login"),
    path("auth/logout", logout_view, name="logout"),
    path("auth/forgot-password", forgot_password_view, name="forgot_password"),
    path("auth/reset-password", reset_password_view, name="reset_password"),
    path("auth/user", user_info_view, name="user_info"),
    # Include the router URLs
    path("", include(router.urls)),
]
