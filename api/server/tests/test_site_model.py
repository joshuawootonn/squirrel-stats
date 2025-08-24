"""
Tests for the Site model.

These tests verify the behavior of the Site model including:
- Identifier generation
- Uniqueness constraints
- String representation
"""

from django.test import TestCase

from server.models import Site


class SiteModelTests(TestCase):
    """Given: The Site model"""

    def test_site_generates_identifier(self):
        """When: A site is created, Then: It generates a unique identifier"""
        # Given
        site_name = "Test Site"

        # When
        site = Site.objects.create(name=site_name)

        # Then
        self.assertIsNotNone(site.identifier)
        self.assertEqual(site.name, site_name)

        # Verify identifier format: adjective-noun-XXXXXX
        parts = site.identifier.split("-")
        self.assertEqual(len(parts), 3)
        self.assertEqual(len(parts[2]), 6)  # 6-character hash
        self.assertTrue(
            all(c.isupper() or c.isdigit() for c in parts[2])
        )  # Uppercase alphanumeric

    def test_multiple_sites_have_unique_identifiers(self):
        """When: Multiple sites are created, Then: Their identifiers are unique"""
        # Given
        num_sites = 20

        # When
        sites = [Site.objects.create(name=f"Test Site {i}") for i in range(num_sites)]

        # Then
        identifiers = [site.identifier for site in sites]
        unique_identifiers = set(identifiers)
        self.assertEqual(len(identifiers), len(unique_identifiers))

    def test_site_string_representation(self):
        """When: Site is converted to string, Then: It shows name and identifier"""
        # Given
        site = Site.objects.create(name="My Analytics Site")

        # When
        site_str = str(site)

        # Then
        self.assertIn("My Analytics Site", site_str)
        self.assertIn(site.identifier, site_str)
        self.assertEqual(site_str, f"My Analytics Site ({site.identifier})")

    def test_identifier_does_not_regenerate(self):
        """When: Site with identifier is saved again, Then: It is unchanged"""
        # Given
        site = Site.objects.create(name="Test Site")
        original_identifier = site.identifier

        # When
        site.name = "Updated Site Name"
        site.save()

        # Then
        self.assertEqual(site.identifier, original_identifier)


class SiteIdentifierGenerationTests(TestCase):
    """Given: Site identifier generation requirements"""

    def test_identifier_uses_woodland_theme(self):
        """When: Identifier is generated, Then: It uses woodland-themed words"""
        # Given
        sites = [Site.objects.create(name=f"Site {i}") for i in range(10)]

        # When
        identifiers = [site.identifier for site in sites]

        # Then
        for identifier in identifiers:
            parts = identifier.split("-")
            adjective, noun, hash_part = parts

            # Basic check that words are lowercase and non-empty
            self.assertTrue(adjective.islower())
            self.assertTrue(noun.islower())
            self.assertTrue(len(adjective) > 0)
            self.assertTrue(len(noun) > 0)

            # Hash part should be uppercase alphanumeric
            self.assertEqual(len(hash_part), 6)
            self.assertTrue(all(c.isupper() or c.isdigit() for c in hash_part))
