# import pytest
# from fastapi.testclient import TestClient
# from api.main import app

# client = TestClient(app)

# # Data for testing
# organization_data = {
#     "name": "pytest_organization",
#     "title": "Pytest Organization",
#     "description": "Organization created for pytest."
# }

# dataset_data = {
#     "dataset_name": "pytest_dataset",
#     "dataset_title": "Pytest Dataset Title",
#     "organization_id": "pytest_organization",
#     "resource_url": "http://example.com/resource",
#     "resource_name": "Pytest Resource Name",
#     "dataset_description": "This is a dataset for testing.",
#     "resource_description": "This is a resource for testing.",
#     "resource_format": "CSV"
# }

# # Global variables to store IDs
# organization_id = None
# dataset_id = None

# @pytest.fixture(scope="module", autouse=True)
# def setup():
#     # Setup code to ensure the organization does not already exist
#     global organization_id
#     response = client.post("/register/organization", json=organization_data)
#     if response.status_code == 201:
#         response_data = response.json()
#         organization_id = response_data["id"]
#     else:
#         existing_org_response = client.get(f"/search/datasource/?organization_id={organization_data['name']}")
#         if existing_org_response.status_code == 200:
#             results = existing_org_response.json()
#             if results:
#                 client.delete("/delete/organization", data={"organization_id": results[0]['id']})
#                 organization_id = None

# @pytest.fixture(scope="module", autouse=True)
# def cleanup():
#     # Teardown code to delete the organization after tests
#     yield
#     if organization_id:
#         client.delete("/delete/organization", data={"organization_id": organization_id})

# # Test to create an organization
# @pytest.mark.order(1)
# def test_create_organization():
#     global organization_id
#     # Ensure the organization does not already exist
#     response = client.get(f"/search/datasource/?organization_id={organization_data['name']}")
#     if response.status_code == 200:
#         results = response.json()
#         if results:
#             client.delete("/delete/organization", data={"organization_id": results[0]['id']})
#             organization_id = None
    
#     # Create the organization
#     response = client.post("/register/organization", json=organization_data)
#     if response.status_code != 201:
#         print(response.json())  # Print the error message if the status code is not 201
#     assert response.status_code == 201  # Expecting 201 Created
#     response_data = response.json()
#     assert "id" in response_data
#     assert "message" in response_data
#     assert response_data["message"] == "Organization created successfully"
#     organization_id = response_data["id"]

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

# Data for testing
organization_data = {
    "name": "pytest_organization",
    "title": "Pytest Organization",
    "description": "Organization created for pytest."
}

# Global variables to store IDs
organization_id = None

@pytest.fixture(scope="module", autouse=True)
def setup_and_cleanup():
    global organization_id

    # Setup: Ensure the organization does not already exist
    existing_org_response = client.get(f"/search/datasource/?organization_id={organization_data['name']}")
    if existing_org_response.status_code == 200:
        results = existing_org_response.json()
        if results:
            delete_response = client.delete("/delete/organization", json={"organization_id": results[0]['id']})
            print(f"Setup: Delete response status: {delete_response.status_code}, body: {delete_response.json()}")
            organization_id = None

    # Ensure the organization is deleted
    existing_org_response = client.get(f"/search/datasource/?organization_id={organization_data['name']}")
    print(f"Setup: Check after delete status: {existing_org_response.status_code}, body: {existing_org_response.json()}")
    
    # Run the tests
    yield

    # Cleanup: Delete the organization after tests
    if organization_id:
        delete_response = client.delete("/delete/organization", json={"organization_id": organization_id})
        print(f"Cleanup: Delete response status: {delete_response.status_code}, body: {delete_response.json()}")

# Test to create an organization
@pytest.mark.order(1)
def test_create_organization():
    global organization_id
    # Create the organization
    response = client.post("/register/organization", json=organization_data)
    if response.status_code != 201:
        print(response.json())  # Print the error message if the status code is not 201
    assert response.status_code == 201  # Expecting 201 Created
    response_data = response.json()
    assert "id" in response_data
    assert "message" in response_data
    assert response_data["message"] == "Organization created successfully"
    organization_id = response_data["id"]




# # Test to register a datasource
# @pytest.mark.order(2)
# def test_register_datasource():
#     global dataset_id
#     response = client.post("/register/datasource", json=dataset_data)
#     assert response.status_code == 201
#     dataset_id = response.json()
#     assert dataset_id is not None

# # Test to search for datasource by name
# @pytest.mark.order(3)
# def test_search_datasource_by_name():
#     response = client.get(f"/search/datasource/?dataset_name={dataset_data['dataset_name']}")
#     assert response.status_code == 200
#     results = response.json()
#     assert len(results) > 0
#     assert results[0]["name"] == dataset_data["dataset_name"]

# # Test to search for datasource by organization ID
# @pytest.mark.order(4)
# def test_search_datasource_by_organization():
#     response = client.get(f"/search/datasource/?organization_id={organization_id}")
#     assert response.status_code == 200
#     results = response.json()
#     assert len(results) > 0
#     assert results[0]["organization_id"] == organization_id

# # Test to search for datasource by search term
# @pytest.mark.order(5)
# def test_search_datasource_by_term():
#     response = client.get(f"/search/datasource/?search_term=Pytest")
#     assert response.status_code == 200
#     results = response.json()
#     assert len(results) > 0
#     assert any("Pytest" in result["title"] for result in results)

# # Test to delete the organization and verify that no datasets are found afterwards
# @pytest.mark.order(6)
# def test_delete_organization():
#     response = client.delete("/delete/organization", data={"organization_id": organization_id})
#     assert response.status_code == 200
#     search_response = client.get(f"/search/datasource/?organization_id={organization_id}")
#     assert search_response.status_code == 200
#     results = search_response.json()
#     assert len(results) == 0
