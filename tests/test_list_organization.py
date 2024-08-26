from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_list_organizations_success():
    response = client.get("/organization")
    assert response.status_code == 200
    
    organizations = response.json()
    assert isinstance(organizations, list)
    assert all(isinstance(org, str) for org in organizations)
