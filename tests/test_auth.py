### ✅ File: tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def test_user():
    return {"username": "testuser", "password": "testpass"}

def test_register(test_user):
    response = client.post("/register", json=test_user)
    assert response.status_code in [200, 400]  # Already exists or successful

def test_login(test_user):
    response = client.post("/token", data=test_user)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_calculate_authenticated(test_user):
    login = client.post("/token", data=test_user)
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"num1": 10, "num2": 5, "operation": "add"}
    response = client.post("/calculate", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["result"] == 15

def test_calculate_unauthenticated():
    payload = {"num1": 10, "num2": 5, "operation": "add"}
    response = client.post("/calculate", json=payload)
    assert response.status_code == 401
