"""
Tests for the page view endpoint (/pv).

These tests verify the behavior of the page view tracking endpoint including:
- Valid tracking requests
- Error handling
- Privacy features
- Request validation
"""

import json

from django.test import Client, TestCase, TransactionTestCase
from server.models import PageView, Site


class SiteExistsTests(TransactionTestCase):
    """Given: A site exists in the system"""

    def setUp(self):
        """Set up test data before each test."""
        self.site = Site.objects.create(name="Test Analytics Site")
        self.client = Client()

    def test_valid_pageview_returns_success(self):
        """When: A valid page view is tracked, Then: It returns success"""
        # Given
        # Site already created in setUp

        # When
        response = self.client.get(
            "/pv",
            {
                "sid": self.site.identifier,
                "h": "https://example.com",
                "p": "/",
                "r": "https://google.com",
            },
        )

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_pageview_creates_record(self):
        """When: A page view is tracked, Then: It creates a PageView record"""
        # Given
        initial_count = PageView.objects.count()

        # When
        self.client.get(
            "/pv",
            {
                "sid": self.site.identifier,
                "h": "https://example.com",
                "p": "/about",
                "r": "https://example.com/",
            },
        )

        # Then
        self.assertEqual(PageView.objects.count(), initial_count + 1)
        page_view = PageView.objects.latest("created_at")
        self.assertEqual(page_view.site, self.site)
        self.assertEqual(page_view.path, "/about")
        self.assertEqual(page_view.url, "https://example.com/about")
        self.assertEqual(page_view.referrer, "https://example.com/")
        self.assertEqual(page_view.referrer_domain, "example.com")

    def test_query_string_included_in_url(self):
        """When: Query string JSON is provided, Then: It includes params in URL"""
        # Given
        query_params = {"search": "django", "category": "web"}

        # When
        self.client.get(
            "/pv",
            {
                "sid": self.site.identifier,
                "h": "https://example.com",
                "p": "/search",
                "qs": json.dumps(query_params),
            },
        )

        # Then
        page_view = PageView.objects.latest("created_at")
        self.assertIn("search=django", page_view.url)
        self.assertIn("category=web", page_view.url)

    def test_invalid_json_logs_warning(self):
        """When: Invalid JSON in query string, Then: It logs warning but continues"""
        # Given
        invalid_json = "{invalid-json}"

        # When
        response = self.client.get(
            "/pv",
            {
                "sid": self.site.identifier,
                "h": "https://example.com",
                "p": "/test",
                "qs": invalid_json,
            },
        )

        # Then
        self.assertEqual(response.status_code, 200)  # Still succeeds
        page_view = PageView.objects.latest("created_at")
        self.assertEqual(page_view.url, "https://example.com/test")  # URL without query params

    def test_post_request_is_accepted(self):
        """When: POST request is made, Then: It returns 200 and ok"""
        # Given
        # Site already created in setUp

        # When
        response = self.client.post(
            "/pv",
            {
                "sid": self.site.identifier,
                "h": "https://example.com",
                "p": "/",
                "qs": json.dumps({}),
            },
        )

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class NoSiteExistsTests(TestCase):
    """Given: No site exists with the provided identifier"""

    def setUp(self):
        self.client = Client()

    def test_invalid_site_identifier_returns_not_found(self):
        """When: Invalid site identifier is used, Then: It returns 404"""
        # Given
        invalid_identifier = "invalid-site-ABC123"

        # When
        response = self.client.get(
            "/pv",
            {
                "sid": invalid_identifier,
                "h": "https://example.com",
                "p": "/",
            },
        )

        # Then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "Invalid site identifier"})

    def test_missing_site_identifier_returns_bad_request(self):
        """When: Site identifier is missing, Then: It returns 400"""
        # Given
        # No site identifier in request

        # When
        response = self.client.get(
            "/pv",
            {
                "h": "https://example.com",
                "p": "/",
            },
        )

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Missing site identifier"})


class PrivacyRequirementsTests(TestCase):
    """Given: Privacy requirements for analytics"""

    def setUp(self):
        self.site = Site.objects.create(name="Privacy Test Site")
        self.client = Client()

    def test_ip_address_stores_hash_only(self):
        """When: IP address is received, Then: It stores only the hash"""
        # Given
        # Django test client doesn't set REMOTE_ADDR by default

        # When
        self.client.get(
            "/pv",
            {
                "sid": self.site.identifier,
                "h": "https://example.com",
                "p": "/privacy-test",
            },
            REMOTE_ADDR="192.168.1.100",
        )

        # Then
        page_view = PageView.objects.latest("created_at")
        self.assertEqual(len(page_view.ip_hash), 64)  # SHA-256 produces 64 char hex
        self.assertNotIn("192.168.1.100", page_view.ip_hash)  # IP not stored in plain text

    def test_no_referrer_stores_empty_string(self):
        """When: No referrer is provided, Then: It stores empty string"""
        # Given
        # No referrer in request

        # When
        self.client.get(
            "/pv",
            {
                "sid": self.site.identifier,
                "h": "https://example.com",
                "p": "/direct",
            },
        )

        # Then
        page_view = PageView.objects.latest("created_at")
        self.assertEqual(page_view.referrer, "")
        self.assertEqual(page_view.referrer_domain, "")
