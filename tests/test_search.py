import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.config import keycloak_settings
import random
import string

client = TestClient(app)

def generate_random_name(prefix="test"):
    return f"{prefix}_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def test_create_search_and_delete_datasource_with_org():
    org_name = generate_random_name("org")
    dataset_name = generate_random_name("dataset")
    resource_name = generate_random_name("resource")
    
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

    # Step 2: Create the dataset with resource
    dataset_payload = {
        "resource_name": resource_name,
        "resource_title": "Test Resource Title",
        "owner_org": org_name,
        "resource_s3": "http://example.com/resource",
        "notes": "This is a test resource.",
        "extras": {
            "key1": "value1",
            "key2": "value2"
        }
    }
    
    create_dataset_response = client.post("/s3", json=dataset_payload, headers=headers)
    assert create_dataset_response.status_code == 201
    
    create_dataset_data = create_dataset_response.json()
    assert "id" in create_dataset_data

    # Step 3: Search for the dataset using different parameters
    search_params = {
        "dataset_name": resource_name,
        "dataset_title": "Test Resource Title",
        "owner_org": org_name,
        "resource_url": "http://example.com/resource",
        "resource_name": resource_name,
        "dataset_description": "This is a test dataset.",
        "resource_description": "Resource pointing to http://example.com/resource",
        "resource_format": "s3",
        "search_term": "test",
        "server": "local"
    }
    
    search_response = client.get("/search", params=search_params, headers=headers)
    assert search_response.status_code == 200
    
    search_results = search_response.json()
    assert len(search_results) > 0

    # Step 4: Delete the dataset
    delete_response = client.delete(f"/resource/{resource_name}", headers=headers)
    assert delete_response.status_code == 200
    
    delete_data = delete_response.json()
    assert "deleted successfully" in delete_data["message"]

    # Step 5: Delete the organization
    delete_org_response = client.delete(f"/organization/{org_name}", headers=headers)
    assert delete_org_response.status_code == 200
    
    delete_org_data = delete_org_response.json()
    assert delete_org_data["message"] == "Organization deleted successfully"

def test_create_search_and_delete_timestamped_datasource_with_org():
    org_name = generate_random_name("org")
    dataset_name = generate_random_name("dataset")
    resource_name = generate_random_name("resource")
    
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
    # Step 2: Create datasets with resource
    test_resources = [
        (generate_random_name(), "http://example.com/resource1.nc", "2024-10-03T10:30"),
        (generate_random_name(), "http://example.com/resource2.nc", "2024-10-03T11:30"),
        (generate_random_name(), "http://example.com/resource3.nc", "2024-10-03T12:30")
    ]
    extra_key = generate_random_name()
    extra_val = generate_random_name()
    for (resource_name, resource_url, timestamp) in test_resources:
        url_payload = {
            "resource_name": resource_name,
            "resource_title": "Timestamped Resource Test",
            "owner_org": org_name,
            "resource_url": resource_url,
            "file_type": "NetCDF",
            "extras": {
                extra_key: extra_val,
                "timestamp": timestamp
            }
        }
        create_url_response = client.post("/url", json=url_payload, headers=headers)
        assert create_url_response.status_code == 201
    
        create_dataset_data = create_url_response.json()
        assert "id" in create_dataset_data

    # Step 3: Search for the dataset using different parameters

    # Step 3a: all results come back
    search_params = {
        "filter_list": [f"{extra_key}:{extra_val}"]
    }

    search_response = client.post("/search", json=search_params, headers=headers)
    assert search_response.status_code == 200
    
    search_results = search_response.json()
    assert len(search_results) == 3

    # Step 3b: first result later than 11:15 come back
    search_params = {
        "filter_list": [f"{extra_key}:{extra_val}"],
        "timestamp": ">2024-10-03T11:15"
    }

    search_response = client.post("/search", json=search_params, headers=headers)
    assert search_response.status_code == 200
    
    search_results = search_response.json()
    assert len(search_results) == 1

    timestep = search_results[0]["extras"]["timestamp"]
    assert timestep == "2024-10-03T11:30"

    # Step 3c: first result earlier than 11:15 come back
    search_params = {
        "filter_list": [f"{extra_key}:{extra_val}"],
        "timestamp": "<2024-10-03T11:15"
    }

    search_response = client.post("/search", json=search_params, headers=headers)
    assert search_response.status_code == 200
    
    search_results = search_response.json()
    assert len(search_results) == 1

    timestep = search_results[0]["extras"]["timestamp"]
    assert timestep == "2024-10-03T10:30"

    # Step 3d: all result later than 11:15 come back
    search_params = {
        "filter_list": [f"{extra_key}:{extra_val}"],
        "timestamp": "2024-10-03T11:15/"
    }

    search_response = client.post("/search", json=search_params, headers=headers)
    assert search_response.status_code == 200
    
    search_results = search_response.json()
    assert len(search_results) == 2

    # Step 3e: all result earlier than 11:15 come back
    search_params = {
        "filter_list": [f"{extra_key}:{extra_val}"],
        "timestamp": "/2024-10-03T11:15"
    }

    search_response = client.post("/search", json=search_params, headers=headers)
    assert search_response.status_code == 200
    
    search_results = search_response.json()
    assert len(search_results) == 1
    
    # Step 4: Delete the datasets
    for (resource_name, *_) in test_resources:
        delete_response = client.delete(f"/resource/{resource_name}", headers=headers)
        assert delete_response.status_code == 200
    
    delete_data = delete_response.json()
    assert "deleted successfully" in delete_data["message"]

    # Step 5: Delete the organization
    delete_org_response = client.delete(f"/organization/{org_name}", headers=headers)
    assert delete_org_response.status_code == 200
    
    delete_org_data = delete_org_response.json()
    assert delete_org_data["message"] == "Organization deleted successfully"
