import random
import string
import requests
import pytest
import time

# Constants
API_URL = "http://localhost:8000"
OWNER_ORG = "test_org1"
USERNAME = "placeholder@placeholder.com"
PASSWORD = "placeholder"

# Function to generate a unique resource name
def generate_unique_resource_name(prefix):
    return prefix + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

# Function to get auth token
def get_auth_token(api_url, username, password):
    endpoint = f"{api_url}/token"
    response = requests.post(endpoint, data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to retrieve auth token. Status code: {response.status_code}, Response: {response.text}")
        response.raise_for_status()

# Function to post URL resource data to CKAN
def post_url_resource(api_url, resource_data, headers):
    endpoint = f"{api_url}/url"
    response = requests.post(endpoint, json=resource_data, headers=headers)
    if response.status_code == 201:
        print("Resource created successfully:", response.json())
        return response.json()
    else:
        print("Error creating resource:", response.status_code, response.json())
        response.raise_for_status()

# Function to get URL resources from CKAN
def get_url_resources(api_url, headers):
    endpoint = f"{api_url}/search"
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        resources = response.json()
        return resources
    else:
        print(f"Failed to retrieve resources. Status code: {response.status_code}, Response: {response.text}")
        response.raise_for_status()

# Function to update URL resource data in CKAN
def put_url_resource(api_url, resource_id, update_data, headers):
    endpoint = f"{api_url}/url/{resource_id}"
    response = requests.put(endpoint, json=update_data, headers=headers)
    if response.status_code == 200:
        print("Resource updated successfully:", response.json())
        return response.json()
    else:
        print("Error updating resource:", response.status_code, response.json())
        response.raise_for_status()

# Function to delete URL resource from CKAN
def delete_resource(api_url, resource_id, headers):
    endpoint = f"{api_url}/dataset/{resource_id}"
    response = requests.delete(endpoint, headers=headers)
    if response.status_code == 200:
        print("Resource deleted successfully:", response.json())
        return response.json()
    else:
        print("Error deleting resource:", response.status_code, response.json())
        response.raise_for_status()

# Pytest test function for URL
@pytest.mark.asyncio
async def test_url_ckan_integration():
    # Get auth token
    token = get_auth_token(API_URL, USERNAME, PASSWORD)
    headers = {"Authorization": f"Bearer {token}"}

    # Generate a unique resource name
    resource_name = generate_unique_resource_name("url_example_")

    # Step 2: Register URL resource as dataset in CKAN
    resource_data = {
        "resource_name": resource_name,
        "resource_title": "Random URL Example",
        "owner_org": OWNER_ORG,
        "resource_url": "http://example.com/resource",
        "notes": "This is a randomly generated URL resource registered as a CKAN dataset."
    }
    created_resource = post_url_resource(API_URL, resource_data, headers)
    resource_id = created_resource["id"]

    # Add a delay to ensure the resource is indexed
    time.sleep(2)

    # Step 3: Retrieve URL resource information from CKAN
    url_resources = get_url_resources(API_URL, headers)
    resource_info = next((res for res in url_resources if res['name'] == resource_name), None)
    assert resource_info is not None

    # Step 4: Update URL resource
    update_data = {
        "resource_title": "Updated Random URL Example",
        "notes": "This is an updated description.",
        "extras": {"new_key": "new_value"}
    }
    put_url_resource(API_URL, resource_id, update_data, headers)

    # Add a delay to ensure the resource is updated
    time.sleep(2)

    # Step 5: Verify the update
    updated_resources = get_url_resources(API_URL, headers)
    updated_resource_info = next((res for res in updated_resources if res['name'] == resource_name), None)
    assert updated_resource_info is not None
    assert updated_resource_info["title"] == "Updated Random URL Example"
    assert updated_resource_info["notes"] == "This is an updated description."
    assert "new_key" in updated_resource_info["extras"]
    assert updated_resource_info["extras"]["new_key"] == "new_value"

    # Step 6: Delete URL resource
    delete_resource(API_URL, resource_id, headers)

    # Add a delay to ensure the resource is deleted
    time.sleep(2)

    # Step 7: Verify the deletion
    deleted_resources = get_url_resources(API_URL, headers)
    deleted_resource_info = next((res for res in deleted_resources if res['name'] == resource_name), None)
    assert deleted_resource_info is None

if __name__ == "__main__":
    pytest.main([__file__])
