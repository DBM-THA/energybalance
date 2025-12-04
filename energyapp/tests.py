from django.test import TestCase
from django.urls import reverse
from .models import Building
class SimpleTest(TestCase):

    def test_homepage_status_code(self):
        """Check that the homepage returns HTTP 200."""
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
