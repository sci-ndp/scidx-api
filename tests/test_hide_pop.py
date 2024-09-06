from fastapi.testclient import TestClient
import requests
from api.main import app
from api.config import swagger_settings, keycloak_settings

client = TestClient(app)

def get_test_user_token():
    url = f"{keycloak_settings.keycloak_url}/realms/{keycloak_settings.realm_name}/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": keycloak_settings.client_id,
        "client_secret": keycloak_settings.client_secret,
        "username": "placeholder@placeholder.com",
        "password": "placeholder"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

def test_pop_configuration():
    token = get_test_user_token()
    
    headers = {
        "Authorization": f"Bearer {token}"
    }

    if swagger_settings.pop:  # Check if POP is True
        # Test POST /stream endpoint is hidden
        post_stream_response = client.post("/stream", json={"data": "test"}, headers=headers)
        assert post_stream_response.status_code == 404

        # Test GET /stream endpoint is hidden
        get_stream_response = client.get("/stream", headers=headers)
        assert get_stream_response.status_code == 404
    else:  # POP is False
        # Test POST /stream endpoint is available
        post_stream_response = client.post("/stream", json={"data": "test"}, headers=headers)
        assert post_stream_response.status_code != 404
        
        # Test GET /stream endpoint is available
        get_stream_response = client.get("/stream", headers=headers)
        assert get_stream_response.status_code != 404
