from fastapi.testclient import TestClient
from api.main import app
from api.config import swagger_settings, keycloak_settings

client = TestClient(app)

def test_pop_configuration():
    headers = {
        "Authorization": f"Bearer {keycloak_settings.test_username}"
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