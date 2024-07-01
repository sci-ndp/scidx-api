import requests

# Base URL for the API
base_url = "http://127.0.0.1:8000"

# Create an organization
organization_name = input("Enter the name for the organization: ")
organization_data = {
    "name": organization_name,
    "title": input("Enter the title for the organization: "),
    "description": input("Enter a description for the organization: ")
}

response = requests.post(f"{base_url}/organization", json=organization_data)
if response.status_code == 201:
    organization_id = response.json()["id"]
    print(f"Organization created successfully with ID: {organization_id}")
else:
    print(f"Error: {response.json()['detail']}")

# Register a datasource
dataset_data = {
    "dataset_name": input("Enter the dataset name: "),
    "dataset_title": input("Enter the dataset title: "),
    "owner_org": organization_name,
    "resource_url": input("Enter the resource URL: "),
    "resource_name": input("Enter the resource name: "),
    "dataset_description": input("Enter the dataset description: "),
    "resource_description": input("Enter the resource description: "),
    "resource_format": input("Enter the resource format (e.g., CSV): ")
}

response = requests.post(f"{base_url}/datasource", json=dataset_data)
if response.status_code == 201:
    dataset_id = response.json()["id"]
    print(f"Dataset created successfully with ID: {dataset_id}")
else:
    print(f"Error: {response.json()['detail']}")

# Search for the dataset by name
dataset_name = input("Enter the dataset name to search for: ")
response = requests.get(f"{base_url}/datasource", params={"dataset_name": dataset_name})
if response.status_code == 200:
    results = response.json()
    print(f"Datasets found by name: {results}")
else:
    print(f"Error: {response.json()['detail']}")

# Search for the dataset by organization name
response = requests.get(f"{base_url}/datasource", params={"owner_org": organization_name})
if response.status_code == 200:
    results = response.json()
    print(f"Datasets found by organization: {results}")
else:
    print(f"Error: {response.json()['detail']}")

# Search for the dataset by term
search_term = input("Enter the search term: ")
response = requests.get(f"{base_url}/datasource", params={"search_term": search_term})
if response.status_code == 200:
    results = response.json()
    print(f"Datasets found by term: {results}")
else:
    print(f"Error: {response.json()['detail']}")

# List all organizations
response = requests.get(f"{base_url}/organization")
if response.status_code == 200:
    organizations = response.json()
    print(f"Organizations: {organizations}")
else:
    print(f"Error: {response.json()['detail']}")

# Delete the organization
response = requests.delete(f"{base_url}/organization/{organization_name}")
if response.status_code == 200:
    print(f"Organization deleted successfully.")
else:
    print(f"Error: {response.json()['detail']}")
