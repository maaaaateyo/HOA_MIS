from django.test import TestCase
from django.conf import settings
import requests
import base64

class PayMongoIntegrationTest(TestCase):
    def setUp(self):
        self.url = "https://api.paymongo.com/v1/links"
        self.payload = {
            "data": {
                "attributes": {
                    "amount": 28000,
                    "description": "Monthly Dues Payment",
                    "remarks": "GCASH Payment"
                }
            }
        }
        secret_key = settings.PAYMONGO_SECRET_KEY
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {base64.b64encode(secret_key.encode()).decode()}",
        }

    def test_paymongo_payment_link_creation(self):
        """Test creating a payment link with PayMongo API."""
        response = requests.post(self.url, json=self.payload, headers=self.headers)
        self.assertEqual(response.status_code, 201, "Payment link creation failed")
        response_data = response.json()
        self.assertIn("data", response_data, "Response does not contain 'data' key")
        self.assertIn("attributes", response_data["data"], "Response data missing 'attributes' key")
