import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from api.main import app

# Create a test client
client = TestClient(app)

# Example data for testing
example_data = {
    "dataset_name": "example_dataset_name",
    "dataset_title": "Example Dataset Title",
    "organization_id": "example_org_id",
    "resource_url": "http://example.com/resource",
    "resource_name": "Example Resource Name",
    "dataset_description": "This is an example dataset.",
    "resource_description": "This is an example resource.",
    "resource_format": "CSV"
}

def test_create_datasource_success():
    # Mock the add_datasource function to return a simulated ID
    with patch(
        'api.services.datasource_services.add_datasource',
        return_value="12345678-abcd-efgh-ijkl-1234567890ab"):
        response = client.post("/datasource/", json=example_data)
    
    # Check that the response status code is 201 (Created)
    assert response.status_code == 201
    # Check that the response content is the simulated ID
    assert response.json() == "12345678-abcd-efgh-ijkl-1234567890ab"

def test_create_datasource_failure(): 
    # Mock the add_datasource function to raise an exception
    with patch(
        'api.services.datasource_services.add_datasource',
        side_effect=Exception("Error creating dataset")):
        response = client.post("/datasource/", json=example_data)
    
    # Check that the response status code is 400 (Bad Request)
    assert response.status_code == 400
    # Check that the response content contains the expected error message
    assert response.json() == {"detail": "Error creating dataset"}

# Run the tests
if __name__ == "__main__":
    pytest.main()
