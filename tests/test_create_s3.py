import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.config import keycloak_settings
import random
import string

client = TestClient(app)

def generate_random_name(prefix="test"):
    return f"{prefix}_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def test_create_and_delete_s3_resource_with_org():
    org_name = generate_random_name("org")
    resource_name = generate_random_name("s3_resource")
    
    headers = {
        "Authorization": f"Bearer {keycloak_settings.test_username}"
    }
    
    # Step 1: Create the organization
    org_payload = {
        "name": org_name,
        "title": "Test Organization",
        "description": "This is a test organization."
    }
    
    create_org_response = client.post("/organization", json=org_payload, headers=headers)
    assert create_org_response.status_code == 201
    
    create_org_data = create_org_response.json()
    assert "id" in create_org_data

    # Step 2: Create the S3 resource under the new organization
    s3_payload = {
        "resource_name": resource_name,
        "resource_title": "S3 Resource Test",
        "owner_org": org_name,
        "resource_s3": "http://example.com/resource",
        "notes": "This is a test S3 resource.",
        "extras": {
            "key1": "value1",
            "key2": "value2"
        }
    }
    
    create_s3_response = client.post("/s3", json=s3_payload, headers=headers)
    assert create_s3_response.status_code == 201
    
    create_s3_data = create_s3_response.json()
    assert "id" in create_s3_data

    # Verify the ID of the created resource
    resource_id = create_s3_data["id"]
    print(f"Resource created with ID: {resource_id}")

    # Step 3: Delete the S3 resource
    delete_response = client.delete(f"/resource/{resource_name}", headers=headers)
    
    # Print the error detail if the deletion fails
    if delete_response.status_code != 200:
        print(f"Error deleting resource: {delete_response.json()}")
    
    assert delete_response.status_code == 200
    
    delete_data = delete_response.json()
    assert "deleted successfully" in delete_data["message"]

    # Step 4: Delete the organization
    delete_org_response = client.delete(f"/organization/{org_name}", headers=headers)
    assert delete_org_response.status_code == 200
    
    delete_org_data = delete_org_response.json()
    assert delete_org_data["message"] == "Organization deleted successfully"
