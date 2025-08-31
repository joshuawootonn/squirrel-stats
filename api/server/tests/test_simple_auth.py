"""
Tests for Django basic authentication.
"""

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from server.models import Site


class AuthTest(TestCase):
    """Test authentication flow."""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_authentication_success(self):
        """Test successful basic authentication."""
        # Make authenticated request using basic auth
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/sites/")

        # Should succeed (empty list since no sites)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 0)

    def test_no_authentication(self):
        """Test request without authentication fails."""
        response = self.client.get("/api/v1/sites/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_credentials(self):
        """Test invalid credentials fail authentication."""
        # Use invalid credentials
        import base64

        credentials = base64.b64encode(b"invalid:credentials").decode("ascii")
        self.client.credentials(HTTP_AUTHORIZATION=f"Basic {credentials}")
        response = self.client.get("/api/v1/sites/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SiteOwnershipTest(TestCase):
    """Test site ownership by user."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create users
        self.alice = User.objects.create_user(username="alice", password="alicepass123")
        self.bob = User.objects.create_user(username="bob", password="bobpass123")
        self.charlie = User.objects.create_user(username="charlie", password="charliepass123")

        # Create sites for different users
        Site.objects.create(user=self.alice, name="Alice's Site", identifier="alice-site-ABC123")
        Site.objects.create(user=self.bob, name="Bob's Site", identifier="bob-site-DEF456")

    def test_user_sees_only_own_sites(self):
        """Test users can only see their own sites."""
        # Authenticate as Alice
        self.client.force_authenticate(user=self.alice)
        response = self.client.get("/api/v1/sites/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["name"], "Alice's Site")

    def test_create_site_assigns_user(self):
        """Test creating a site assigns the correct user."""
        # Authenticate as Charlie
        self.client.force_authenticate(user=self.charlie)
        response = self.client.post("/api/v1/sites/", {"name": "Charlie's New Site"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify site was created with correct user
        site = Site.objects.get(name="Charlie's New Site")
        self.assertEqual(site.user, self.charlie)

    def test_site_limit_per_user(self):
        """Test site limit is enforced per user."""
        # Create a user for this test
        dave = User.objects.create_user(username="dave", password="davepass123")

        # Create 50 sites for Dave
        for i in range(50):
            Site.objects.create(user=dave, name=f"Dave's Site {i}", identifier=f"dave-{i}-XYZ")

        self.client.force_authenticate(user=dave)
        response = self.client.post("/api/v1/sites/", {"name": "Dave's 51st Site"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Site limit reached", response.json()["error"])
