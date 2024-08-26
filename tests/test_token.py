import pytest
from fastapi.testclient import TestClient
from api.main import app  # Asegúrate de que este sea el path correcto hacia tu aplicación FastAPI
from api.config import keycloak_settings

client = TestClient(app)

def test_login_for_access_token_success():
    response = client.post(
        "/token",
        data={"username": keycloak_settings.test_username, "password": keycloak_settings.test_password}
    )
    assert response.status_code == 200
    assert response.json()["access_token"] == keycloak_settings.test_password
    assert response.json()["token_type"] == "bearer"

def test_login_for_access_token_failure():
    response = client.post(
        "/token",
        data={"username": "wronguser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"