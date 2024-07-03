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

# Function to post S3 resource data to CKAN
def post_s3_resource(api_url, resource_data, headers):
    endpoint = f"{api_url}/s3"
    response = requests.post(endpoint, json=resource_data, headers=headers)
    if response.status_code == 201:
        print("Resource created successfully:", response.json())
        return response.json()
    else:
        print("Error creating resource:", response.status_code, response.json())
        response.raise_for_status()

# Function to get S3 resources from CKAN
def get_s3_resources(api_url, headers):
    endpoint = f"{api_url}/search"
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        resources = response.json()
        return resources
    else:
        print(f"Failed to retrieve resources. Status code: {response.status_code}, Response: {response.text}")
        response.raise_for_status()

# Function to update S3 resource data in CKAN
def put_s3_resource(api_url, resource_id, update_data, headers):
    endpoint = f"{api_url}/s3/{resource_id}"
    response = requests.put(endpoint, json=update_data, headers=headers)
    if response.status_code == 200:
        print("Resource updated successfully:", response.json())
        return response.json()
    else:
        print("Error updating resource:", response.status_code, response.json())
        response.raise_for_status()

# Function to delete S3 resource from CKAN
def delete_resource(api_url, resource_id, headers):
    endpoint = f"{api_url}/dataset/{resource_id}"
    response = requests.delete(endpoint, headers=headers)
    if response.status_code == 200:
        print("Resource deleted successfully:", response.json())
        return response.json()
    else:
        print("Error deleting resource:", response.status_code, response.json())
        response.raise_for_status()

# Pytest test function for S3
@pytest.mark.asyncio
async def test_s3_ckan_integration():
    # Get auth token
    token = get_auth_token(API_URL, USERNAME, PASSWORD)
    headers = {"Authorization": f"Bearer {token}"}

    # Generate a unique resource name
    resource_name = generate_unique_resource_name("s3_example_")

    # Step 2: Register S3 resource as dataset in CKAN
    resource_data = {
        "resource_name": resource_name,
        "resource_title": "Random S3 Example",
        "owner_org": OWNER_ORG,
        "resource_s3": "http://example.com/resource",
        "notes": "This is a randomly generated S3 resource registered as a CKAN dataset."
    }
    created_resource = post_s3_resource(API_URL, resource_data, headers)
    resource_id = created_resource["id"]

    # Add a delay to ensure the resource is indexed
    time.sleep(2)

    # Step 3: Retrieve S3 resource information from CKAN
    s3_resources = get_s3_resources(API_URL, headers)
    resource_info = next((res for res in s3_resources if res['name'] == resource_name), None)
    assert resource_info is not None

    # Step 4: Update S3 resource
    update_data = {
        "resource_title": "Updated Random S3 Example",
        "notes": "This is an updated description.",
        "extras": {"new_key": "new_value"}
    }
    put_s3_resource(API_URL, resource_id, update_data, headers)

    # Add a delay to ensure the resource is updated
    time.sleep(2)

    # Step 5: Verify the update
    updated_resources = get_s3_resources(API_URL, headers)
    updated_resource_info = next((res for res in updated_resources if res['name'] == resource_name), None)
    assert updated_resource_info is not None
    assert updated_resource_info["title"] == "Updated Random S3 Example"
    assert updated_resource_info["notes"] == "This is an updated description."
    assert "new_key" in updated_resource_info["extras"]
    assert updated_resource_info["extras"]["new_key"] == "new_value"

    # Step 6: Delete S3 resource
    delete_resource(API_URL, resource_id, headers)

    # Add a delay to ensure the resource is deleted
    time.sleep(2)

    # Step 7: Verify the deletion
    deleted_resources = get_s3_resources(API_URL, headers)
    deleted_resource_info = next((res for res in deleted_resources if res['name'] == resource_name), None)
    assert deleted_resource_info is None

if __name__ == "__main__":
    pytest.main([__file__])
