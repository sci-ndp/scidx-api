import pytest
from fastapi.testclient import TestClient
from api.main import app
import requests
from api.config.keycloak_settings import keycloak_settings

client = TestClient(app)

def get_valid_user_token():
    url = f"{keycloak_settings.keycloak_url}/realms/{keycloak_settings.realm_name}/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": keycloak_settings.client_id,
        "client_secret": keycloak_settings.client_secret,
        "username": "placeholder@placeholder.com",  # Use a valid username
        "password": "placeholder"  # Use the valid password for the user
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

def test_login_for_access_token_failure():
    # Test incorrect credentials
    response = client.post(
        "/token",
        data={"username": "wronguser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_login_for_access_token_success():
    # Test correct credentials
    response = client.post(
        "/token",
        data={"username": "placeholder@placeholder.com", "password": "placeholder"}  # Use correct credentials here
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
