"""
Tests for simplified Clerk authentication.
"""

from unittest.mock import Mock, patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from server.models import Site


class AuthTest(TestCase):
    """Test authentication flow."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()

    @patch("server.auth.authentication.settings.CLERK_CLIENT")
    def test_authentication_success(self, mock_clerk):
        """Test successful authentication extracts user_id."""
        # Mock Clerk session
        mock_session = Mock()
        mock_session.user_id = "user_123"
        mock_clerk.sessions.verify.return_value = mock_session

        # Make authenticated request
        self.client.credentials(HTTP_AUTHORIZATION="Bearer valid_token")
        response = self.client.get("/api/v1/sites/")

        # Should succeed (empty list since no sites)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 0)

    def test_no_authentication(self):
        """Test request without authentication fails."""
        response = self.client.get("/api/v1/sites/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("server.auth.authentication.settings.CLERK_CLIENT")
    def test_invalid_token(self, mock_clerk):
        """Test invalid token fails authentication."""
        mock_clerk.sessions.verify.side_effect = Exception("Invalid token")

        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid_token")
        response = self.client.get("/api/v1/sites/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SiteOwnershipTest(TestCase):
    """Test site ownership by user_id."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create sites for different users
        Site.objects.create(user_id="user_alice", name="Alice's Site", identifier="alice-site-ABC123")
        Site.objects.create(user_id="user_bob", name="Bob's Site", identifier="bob-site-DEF456")

    @patch("server.auth.authentication.settings.CLERK_CLIENT")
    def test_user_sees_only_own_sites(self, mock_clerk):
        """Test users can only see their own sites."""
        # Mock Alice's session
        mock_session = Mock()
        mock_session.user_id = "user_alice"
        mock_clerk.sessions.verify.return_value = mock_session

        self.client.credentials(HTTP_AUTHORIZATION="Bearer alice_token")
        response = self.client.get("/api/v1/sites/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["name"], "Alice's Site")

    @patch("server.auth.authentication.settings.CLERK_CLIENT")
    def test_create_site_assigns_user_id(self, mock_clerk):
        """Test creating a site assigns the correct user_id."""
        # Mock Charlie's session
        mock_session = Mock()
        mock_session.user_id = "user_charlie"
        mock_clerk.sessions.verify.return_value = mock_session

        self.client.credentials(HTTP_AUTHORIZATION="Bearer charlie_token")
        response = self.client.post("/api/v1/sites/", {"name": "Charlie's New Site"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify site was created with correct user_id
        site = Site.objects.get(name="Charlie's New Site")
        self.assertEqual(site.user_id, "user_charlie")

    @patch("server.auth.authentication.settings.CLERK_CLIENT")
    def test_site_limit_per_user(self, mock_clerk):
        """Test site limit is enforced per user."""
        # Mock Dave's session
        mock_session = Mock()
        mock_session.user_id = "user_dave"
        mock_clerk.sessions.verify.return_value = mock_session

        # Create 50 sites for Dave
        for i in range(50):
            Site.objects.create(user_id="user_dave", name=f"Dave's Site {i}", identifier=f"dave-{i}-XYZ")

        self.client.credentials(HTTP_AUTHORIZATION="Bearer dave_token")
        response = self.client.post("/api/v1/sites/", {"name": "Dave's 51st Site"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Site limit reached", response.json()["error"])
