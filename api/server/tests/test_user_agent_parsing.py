"""
Tests for user agent parsing functionality.

These tests verify that different types of user agents are correctly parsed:
- Desktop browsers
- Mobile devices
- Tablets
- Bots/crawlers
"""

from django.test import Client, TestCase

from server.models import PageView, Site


class UserAgentParsingTests(TestCase):
    """Given: Different types of user agents need to be parsed"""

    def setUp(self):
        self.site = Site.objects.create(name="User Agent Test Site")
        self.client = Client()

    def test_desktop_user_agent_parsing(self):
        """When: Desktop user agent is provided, Then: It parses correctly"""
        # Given
        desktop_user_agents = [
            {
                "ua": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                ),
                "expected_browser": "Chrome",
                "expected_os": "Mac OS X",
                "expected_device": "desktop",
            },
            {
                "ua": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) " "Gecko/20100101 Firefox/89.0"),
                "expected_browser": "Firefox",
                "expected_os": "Windows",
                "expected_device": "desktop",
            },
            {
                "ua": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                ),
                "expected_browser": "Chrome",
                "expected_os": "Linux",
                "expected_device": "desktop",
            },
        ]

        for test_case in desktop_user_agents:
            # When
            self.client.get(
                "/pv",
                {
                    "sid": self.site.identifier,
                    "h": "https://example.com",
                    "p": "/desktop-test",
                },
                HTTP_USER_AGENT=test_case["ua"],
            )

            # Then
            page_view = PageView.objects.latest("created_at")
            self.assertEqual(page_view.browser, test_case["expected_browser"])
            self.assertEqual(page_view.operating_system, test_case["expected_os"])
            self.assertEqual(page_view.device_type, test_case["expected_device"])

    def test_mobile_device_detection(self):
        """When: Mobile user agent is used, Then: It detects mobile device"""
        # Given
        mobile_user_agents = [
            {
                "ua": (
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 "
                    "Mobile/15E148 Safari/604.1"
                ),
                "expected_device": "mobile",
                "expected_browser": "Mobile Safari",
                "expected_os": "iOS",
            },
            {
                "ua": (
                    "Mozilla/5.0 (Linux; Android 11; SM-G991B) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.120 Mobile Safari/537.36"
                ),
                "expected_device": "mobile",
                "expected_browser": "Chrome Mobile",
                "expected_os": "Android",
            },
        ]

        for test_case in mobile_user_agents:
            # When
            self.client.get(
                "/pv",
                {
                    "sid": self.site.identifier,
                    "h": "https://example.com",
                    "p": f"/mobile-{test_case['expected_os']}",
                },
                HTTP_USER_AGENT=test_case["ua"],
            )

            # Then
            pv = PageView.objects.filter(path=f"/mobile-{test_case['expected_os']}").first()
            self.assertIsNotNone(pv)
            self.assertEqual(pv.device_type, test_case["expected_device"])
            self.assertIn(test_case["expected_browser"], pv.browser)
            self.assertEqual(pv.operating_system, test_case["expected_os"])

    def test_tablet_detection(self):
        """When: Tablet user agent is used, Then: It detects tablet device"""
        # Given
        tablet_user_agent = (
            "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 "
            "Mobile/15E148 Safari/604.1"
        )

        # When
        self.client.get(
            "/pv",
            {
                "sid": self.site.identifier,
                "h": "https://example.com",
                "p": "/tablet-test",
            },
            HTTP_USER_AGENT=tablet_user_agent,
        )

        # Then
        page_view = PageView.objects.latest("created_at")
        self.assertEqual(page_view.device_type, "tablet")
        self.assertEqual(page_view.operating_system, "iOS")

    def test_bot_detection(self):
        """When: Bot user agent is used, Then: It marks device type as bot"""
        # Given
        bot_user_agents = [
            ("Mozilla/5.0 (compatible; Googlebot/2.1; " "+http://www.google.com/bot.html)"),
            ("Mozilla/5.0 (compatible; bingbot/2.0; " "+http://www.bing.com/bingbot.htm)"),
            ("facebookexternalhit/1.1 " "(+http://www.facebook.com/externalhit_uatext.php)"),
            ("Mozilla/5.0 (compatible; AhrefsBot/7.0; " "+http://ahrefs.com/robot/)"),
        ]

        # When
        for ua in bot_user_agents:
            self.client.get(
                "/pv",
                {
                    "sid": self.site.identifier,
                    "h": "https://example.com",
                    "p": "/bot-test",
                },
                HTTP_USER_AGENT=ua,
            )

        # Then
        bot_views = PageView.objects.filter(site=self.site, device_type="bot", path="/bot-test")
        self.assertEqual(bot_views.count(), 4)
