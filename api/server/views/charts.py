"""
Charts API views for analytics data visualization.

Provides endpoints for fetching aggregated analytics data in formats
suitable for rendering charts and graphs.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from server.auth.authentication import ClerkAuthentication
from server.models import HourlyPageViewStats, Site

logger = logging.getLogger(__name__)


@api_view(["GET"])
@authentication_classes([ClerkAuthentication])
@permission_classes([IsAuthenticated])
def chart_data(request):
    """
    Get hourly pageview data for chart.

    Query Parameters:
    - site_id: Site UUID (required)
    - range: Time range - 'today', 'yesterday', '7d', '30d' (default: 'today')
    - timezone_offset: Client timezone offset in minutes from UTC (optional)

    Returns:
    {
        "hours": [
            {
                "hour": "2024-01-15T14:00:00Z",
                "hour_display": "2:00 PM",  // Adjusted for timezone if provided
                "pageviews": 42,
                "unique_sessions": 15
            },
            ...
        ],
        "total_pageviews": 150,
        "total_unique_sessions": 45,
        "range": "today",
        "timezone_offset": -480  // If provided
    }
    """
    try:
        # Get user ID from authenticated request
        user_id = request.user_id

        # Get parameters
        site_id = request.GET.get("site_id")
        time_range = request.GET.get("range", "today")
        timezone_offset = request.GET.get("timezone_offset")  # Minutes from UTC

        if timezone_offset:
            try:
                timezone_offset = int(timezone_offset)
            except (ValueError, TypeError):
                timezone_offset = None

        # Validate required parameters
        if not site_id:
            return Response({"error": "site_id parameter is required"}, status=400)

        # Validate time range
        valid_ranges = ["today", "yesterday", "7d", "30d"]
        if time_range not in valid_ranges:
            return Response({"error": f"Invalid range. Must be one of: {', '.join(valid_ranges)}"}, status=400)

        # Get the site and verify ownership
        try:
            site = Site.objects.get(id=site_id, user_id=user_id)
        except Site.DoesNotExist:
            return Response({"error": "Site not found or access denied"}, status=404)

        # Calculate time range
        start_time, end_time = _calculate_time_range(time_range, timezone_offset)

        # Get hourly stats
        hourly_data = _get_hourly_data(site, start_time, end_time, timezone_offset)

        # Calculate totals
        total_pageviews = sum(hour["pageviews"] for hour in hourly_data)
        total_unique_sessions = sum(hour["unique_sessions"] for hour in hourly_data)

        response_data = {
            "hours": hourly_data,
            "total_pageviews": total_pageviews,
            "total_unique_sessions": total_unique_sessions,
            "range": time_range,
        }

        if timezone_offset is not None:
            response_data["timezone_offset"] = timezone_offset

        return Response(response_data)

    except Exception as e:
        logger.error(f"Error in chart_data: {e}", exc_info=True)
        return Response({"error": "Internal server error"}, status=500)


def _calculate_time_range(time_range: str, timezone_offset: int = None) -> tuple[datetime, datetime]:
    """
    Calculate start and end times for the given range.

    Args:
        time_range: One of 'today', 'yesterday', '7d', '30d'
        timezone_offset: Client timezone offset in minutes from UTC

    Returns:
        tuple: (start_time, end_time) in UTC
    """
    now = timezone.now()

    # If timezone offset is provided, adjust the "now" to client timezone for day calculations
    if timezone_offset is not None:
        # Convert offset from minutes to timedelta
        client_now = now - timedelta(minutes=timezone_offset)
    else:
        client_now = now

    if time_range == "today":
        # Start of today in client timezone, converted back to UTC
        start_of_day = client_now.replace(hour=0, minute=0, second=0, microsecond=0)
        if timezone_offset is not None:
            start_of_day = start_of_day + timedelta(minutes=timezone_offset)

        start_time = start_of_day
        end_time = start_of_day + timedelta(days=1)

    elif time_range == "yesterday":
        # Start of yesterday in client timezone
        start_of_yesterday = client_now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        if timezone_offset is not None:
            start_of_yesterday = start_of_yesterday + timedelta(minutes=timezone_offset)

        start_time = start_of_yesterday
        end_time = start_of_yesterday + timedelta(days=1)

    elif time_range == "7d":
        # Last 7 days
        start_of_week = client_now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=6)
        if timezone_offset is not None:
            start_of_week = start_of_week + timedelta(minutes=timezone_offset)

        start_time = start_of_week
        end_time = now

    elif time_range == "30d":
        # Last 30 days
        start_of_month = client_now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=29)
        if timezone_offset is not None:
            start_of_month = start_of_month + timedelta(minutes=timezone_offset)

        start_time = start_of_month
        end_time = now

    else:
        raise ValueError(f"Invalid time range: {time_range}")

    return start_time, end_time


def _get_hourly_data(
    site: Site, start_time: datetime, end_time: datetime, timezone_offset: int = None
) -> List[Dict[str, Any]]:
    """
    Get hourly pageview data for the specified time range.

    Args:
        site: Site object
        start_time: Start time (UTC)
        end_time: End time (UTC)
        timezone_offset: Client timezone offset in minutes from UTC

    Returns:
        List of hourly data dictionaries
    """
    # Query hourly stats
    hourly_stats = HourlyPageViewStats.objects.filter(
        site=site,
        hour_bucket__gte=start_time,
        hour_bucket__lt=end_time,
    ).order_by("hour_bucket")

    # Create a mapping of hour buckets to stats
    stats_by_hour = {stats.hour_bucket: stats for stats in hourly_stats}

    # Generate all hours in the range, filling in missing data with zeros
    hourly_data = []
    current_hour = _truncate_to_hour(start_time)
    end_hour = _truncate_to_hour(end_time)

    while current_hour < end_hour:
        stats = stats_by_hour.get(current_hour)

        # Format hour for display (adjust for timezone if provided)
        display_hour = current_hour
        if timezone_offset is not None:
            display_hour = current_hour - timedelta(minutes=timezone_offset)

        hour_data = {
            "hour": current_hour.isoformat(),
            "hour_display": display_hour.strftime("%I:%M %p").lstrip("0"),  # e.g., "2:00 PM"
            "pageviews": stats.pageview_count if stats else 0,
            "unique_sessions": stats.unique_session_count if stats else 0,
        }

        hourly_data.append(hour_data)
        current_hour += timedelta(hours=1)

    return hourly_data


def _truncate_to_hour(dt: datetime) -> datetime:
    """Truncate datetime to the beginning of the hour."""
    return dt.replace(minute=0, second=0, microsecond=0)
