from fastapi.testclient import TestClient
from api.main import app
import requests
from api.config.keycloak_settings import keycloak_settings
import random
import string

client = TestClient(app)

def generate_random_org_name():
    return "test_org_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

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

def test_create_and_delete_organization():
    org_name = generate_random_org_name()
    token = get_test_user_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Step 1: Create the organization
    payload = {
        "name": org_name,
        "title": "Test Organization",
        "description": "This is a test organization."
    }
    
    create_response = client.post("/organization", json=payload, headers=headers)
    assert create_response.status_code == 201
    
    create_data = create_response.json()
    assert "id" in create_data
    assert create_data["message"] == "Organization created successfully"

    # Step 2: Delete the organization
    delete_response = client.delete(f"/organization/{org_name}", headers=headers)
    assert delete_response.status_code == 200
    
    delete_data = delete_response.json()
    assert delete_data["message"] == "Organization deleted successfully"

def test_delete_nonexistent_organization():
    org_name = generate_random_org_name()
    token = get_test_user_token()
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Try to delete a non-existent organization
    delete_response = client.delete(f"/organization/{org_name}", headers=headers)
    assert delete_response.status_code == 400
    
    delete_data = delete_response.json()
    assert delete_data["detail"] == "Organization not found"
