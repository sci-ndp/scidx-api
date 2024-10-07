import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.config import keycloak_settings
import random
import string

client = TestClient(app)

def generate_random_name(prefix="test"):
    return f"{prefix}_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

@pytest.mark.parametrize("file_type,processing", [
    ("stream", {"refresh_rate": "5 seconds", "data_key": "results"}),
    ("CSV", {"delimiter": ",", "header_line": 1, "start_line": 2, "comment_char": "#"}),
    ("TXT", {"delimiter": "\t", "header_line": 1, "start_line": 2}),
    ("JSON", {"info_key": "count", "additional_key": "", "data_key": "results"}),
    ("NetCDF", {"group": "group_name"}),
])
def test_create_and_delete_url_resource_with_org(file_type, processing):
    org_name = generate_random_name("org")
    resource_name = generate_random_name("url_resource")
    
    headers = {
        "Authorization": f"Bearer {keycloak_settings.test_username}"
    }
   
    resource_url_dict = {
            "stream": "http://example.com/resource",
            "CSV": "http://example.com/resource.csv",
            "TXT": "http://example.com/resource.txt",
            "JSON": "http://example.com/resource.json",
            "NetCDF": "http://example.com/resource.nc"
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

    # Step 2: Create the URL resource under the new organization
    url_payload = {
        "resource_name": resource_name,
        "resource_title": f"{file_type} Resource Test",
        "owner_org": org_name,
        "resource_url": resource_url_dict[file_type],
        "file_type": file_type,
        "notes": "This is a test URL resource.",
        "extras": {
            "key1": "value1",
            "key2": "value2"
        },
        "mapping": {
            "field1": "mapping1",
            "field2": "mapping2"
        },
        "processing": processing
    }
    
    create_url_response = client.post("/url", json=url_payload, headers=headers)
    assert create_url_response.status_code == 201
    
    create_url_data = create_url_response.json()
    assert "id" in create_url_data

    # Verify the ID of the created resource
    resource_id = create_url_data["id"]
    print(f"Resource created with ID: {resource_id}")

    # Step 3: Delete the URL resource
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
