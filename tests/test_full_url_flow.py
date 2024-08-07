import pytest
from fastapi.testclient import TestClient
from api.main import app
import uuid

client = TestClient(app)

# Function to generate a unique organization name
def generate_unique_name(base_name):
    return f"{base_name}_{uuid.uuid4().hex[:6]}"

# Global variables to store IDs and names
organization_id = None
organization_name = generate_unique_name("pytest_organization")
resource_name = generate_unique_name("pytest_resource")

# Data for testing
organization_data = {
    "name": organization_name,
    "title": "Pytest Organization",
    "description": "Organization created for pytest."
}

url_data = {
    "resource_name": resource_name,
    "resource_title": "Pytest Resource Title",
    "owner_org": organization_name,
    "resource_url": "http://example.com/resource",
    "notes": "Resource created for pytest."
}

@pytest.fixture(scope="module", autouse=True)
def setup_and_cleanup():
    global organization_id

    # Setup: Ensure the organization does not already exist
    print("Setup: Checking if the organization already exists")
    existing_org_response = client.get("/organization")
    if existing_org_response.status_code == 200:
        organizations = existing_org_response.json()
        print(f"Setup: Existing organizations: {organizations}")
        if organization_name in organizations:
            print(f"Setup: Organization {organization_name} already exists")
            delete_response = client.delete(f"/organization/{organization_name}")
            print(f"Setup: Delete response status: {delete_response.status_code}, body: {delete_response.json()}")
            organization_id = None
        else:
            print("Setup: Organization does not exist")
            organization_id = None
    else:
        print("Setup: Could not check if organization exists.")
        organization_id = None

    # Run the tests
    yield

    # Cleanup: Delete the organization after tests
    if organization_id:
        delete_response = client.delete(f"/organization/{organization_id}")
        print(f"Cleanup: Delete response status: {delete_response.status_code}, body: {delete_response.json()}")

# Test to create an organization
@pytest.mark.order(1)
def test_create_organization():
    global organization_id
    # Create the organization
    print(f"test_create_organization: Creating organization with name: {organization_name}")
    response = client.post("/organization", json=organization_data)
    if response.status_code != 201:
        print(f"test_create_organization: Error - {response.json()['detail']}")
    assert response.status_code == 201  # Expecting 201 Created
    response_data = response.json()
    assert "id" in response_data
    assert "message" in response_data
    assert response_data["message"] == "Organization created successfully"
    organization_id = response_data["id"]

# Test to register a URL resource
@pytest.mark.order(2)
def test_register_url_resource():
    global url_id
    response = client.post("/url", json=url_data)
    if response.status_code != 201:
        print(f"test_register_url_resource: Error - {response.json()['detail']}")
    assert response.status_code == 201  # Expecting 201 Created
    url_id = response.json()["id"]
    assert url_id is not None

# Test to search for the URL resource by name
@pytest.mark.order(3)
def test_search_url_by_name():
    response = client.get(f"/datasource?dataset_name={url_data['resource_name']}")
    if response.status_code != 200:
        print(f"test_search_url_by_name: Error - {response.json()['detail']}")
    assert response.status_code == 200  # Expecting 200 OK
    results = response.json()
    assert len(results) > 0
    assert results[0]["name"] == url_data["resource_name"]

# Test to search for the URL resource by organization ID
@pytest.mark.order(4)
def test_search_url_by_organization():
    response = client.get(f"/datasource?owner_org={url_data['owner_org']}")
    if response.status_code != 200:
        print(f"test_search_url_by_organization: Error - {response.json()['detail']}")
    assert response.status_code == 200  # Expecting 200 OK
    results = response.json()
    assert len(results) > 0
    assert results[0]["owner_org"] == url_data["owner_org"]

# Test to search for the URL resource by search term
@pytest.mark.order(5)
def test_search_url_by_term():
    search_term = "Pytest"
    response = client.get(f"/datasource?search_term={search_term}")
    if response.status_code != 200:
        print(f"test_search_url_by_term: Error - {response.json()['detail']}")
    assert response.status_code == 200  # Expecting 200 OK
    results = response.json()
    assert len(results) > 0
    assert any(search_term in result["title"] for result in results)

# Test to search for the URL resource by owner_org and other parameters
@pytest.mark.order(6)
def test_search_url_by_owner_org_and_other_params():
    search_term = "Pytest"
    dataset_name = url_data['resource_name']
    response = client.get(f"/datasource?owner_org={url_data['owner_org']}&dataset_name={dataset_name}&search_term={search_term}")
    if response.status_code != 200:
        print(f"test_search_url_by_owner_org_and_other_params: Error - {response.json()['detail']}")
    assert response.status_code == 200  # Expecting 200 OK
    results = response.json()
    print(f"Results: {results}")
    assert len(results) > 0
    assert all(result["owner_org"] == url_data["owner_org"] for result in results if result["owner_org"] is not None)
    assert any(search_term in result["title"] or result["name"] == dataset_name for result in results)