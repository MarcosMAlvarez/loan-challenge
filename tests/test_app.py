"""API tests
"""
import sys

sys.path.append(".")
from unittest import TestCase

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class APITests(TestCase):
    """class for testing api"""

    def test_not_authenticated(self):
        """Test that authentication is needed to call admin endpoints"""
        self.assertEqual(client.get("/admin/").status_code, 401)
        self.assertEqual(client.delete("/admin/").status_code, 401)
        self.assertEqual(client.patch("/admin/").status_code, 401)

    def test_authenticated(self):
        """Test that /token endpoint return a bearer token, and test if it possible
        to access admin's endpoint with it."""
        admin = {"username": "marcos", "password": "pass1"}
        response = client.post("/token/", data=admin).json()
        self.assertEqual(response["token_type"], "bearer")

        response = client.get(
            "/admin/", headers={"Authorization": f"Bearer {response['access_token']}"}
        )
        self.assertEqual(response.status_code, 200)

    def test_check_loan(self):
        """Test check-loan endpoint"""
        user = {
            "dni": 32975120,
            "full_name": "juan perez",
            "genre": "masculino",
            "email": "juan@example.com",
            "loan_amount": 50000,
        }
        response = client.post("/check-loan/", json=user)
        self.assertEqual(response.status_code, 200)

        response_json = response.json()
        self.assertIn(response_json["loan_status"], ["approve", "rejected"])
