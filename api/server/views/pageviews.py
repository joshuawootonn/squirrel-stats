import hashlib
import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from user_agents import parse

from ..models import PageView, Site

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get the client's IP address from the request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # Take the first IP in the chain
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "")
    return ip


def parse_user_agent(user_agent_string):
    """
    Parse user agent string using the user-agents library.
    Returns device information including browser, OS, and device type.
    """
    try:
        user_agent = parse(user_agent_string)

        # Determine device type
        if user_agent.is_bot:
            device_type = "bot"
        elif user_agent.is_mobile:
            device_type = "mobile"
        elif user_agent.is_tablet:
            device_type = "tablet"
        elif user_agent.is_pc:
            device_type = "desktop"
        else:
            device_type = "unknown"

        return {
            "device_type": device_type,
            "browser": user_agent.browser.family or "Unknown",
            "browser_version": user_agent.browser.version_string or "",
            "os": user_agent.os.family or "Unknown",
        }
    except Exception as e:
        logger.warning(f"Failed to parse user agent: {e}. User agent: {user_agent_string}")
        return {
            "device_type": "unknown",
            "browser": "Unknown",
            "browser_version": "",
            "os": "Unknown",
        }


@csrf_exempt
@require_http_methods(["GET", "POST"])
def track_pageview(request):
    """
    Track a page view event. Accepts both GET and POST requests.

    Expected parameters (similar to Fathom):
    - sid: Site identifier (required)
    - h: Hostname (required)
    - p: Path (required)
    - r: Referrer (optional)
    - qs: Query string parameters as JSON (optional)

    Returns a JSON response.
    """
    try:
        # Extract parameters
        # Prefer query string values; merge POST body for beacon/form clients
        params = request.GET.copy()
        if request.method == "POST":
            for key in request.POST.keys():
                if key not in params:
                    params[key] = request.POST.get(key)

        # Get required parameters
        site_identifier = params.get("sid")
        hostname = params.get("h", "")
        path = params.get("p", "/")
        referrer = params.get("r", "")
        query_string = params.get("qs", "{}")

        # Validate required parameters
        if not site_identifier:
            return JsonResponse({"error": "Missing site identifier"}, status=400)

        # Find the site
        try:
            site = Site.objects.get(identifier=site_identifier)
        except Site.DoesNotExist:
            return JsonResponse({"error": "Invalid site identifier"}, status=404)

        # Build full URL
        url = hostname + path
        if query_string and query_string != "{}":
            try:
                qs_data = json.loads(query_string)
                if qs_data:
                    # Convert query string dict to URL parameters
                    qs_params = "&".join([f"{k}={v}" for k, v in qs_data.items()])
                    url += "?" + qs_params
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse query string JSON: {e}. Raw qs: {query_string}")
            except Exception as e:
                logger.warning(f"Unexpected error parsing query string: {e}")

        # Get client information
        ip_address = get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")

        # Hash the IP address for privacy
        ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()

        # Parse user agent for basic device info
        device_info = parse_user_agent(user_agent)

        # Create the page view
        PageView.objects.create(
            site=site,
            url=url,
            path=path,
            referrer=referrer,
            ip_hash=ip_hash,
            user_agent=user_agent,
            browser=device_info.get("browser", ""),
            browser_version=device_info.get("browser_version", ""),
            operating_system=device_info.get("os", ""),
            device_type=device_info.get("device_type", "unknown"),
        )

        # Always return JSON response
        return JsonResponse({"status": "ok"}, status=200)

    except Exception as e:
        logger.error(f"Error tracking page view: {e}", exc_info=True)
        return JsonResponse({"error": "Internal error"}, status=500)
