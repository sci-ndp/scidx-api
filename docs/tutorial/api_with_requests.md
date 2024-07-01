# Tutorial: Using the scidx-api with Python and Requests

This tutorial will guide you through using the scidx-api for creating, searching, and managing datasets and organizations using Python's `requests` library.

## Prerequisites

Before starting, make sure you have:
1. An instance of CKAN running.
2. The scidx-api running. You can start the API with:

```bash
uvicorn api.main:app --reload
```

3. Python installed on your machine.
4. The `requests` library installed. You can install it using:

```bash
pip install requests
```

## Base URL

The base URL for the API is `http://127.0.0.1:8000`.

## Understanding Organizations

In CKAN, an organization is a way to group datasets and manage them collectively. It helps in organizing datasets related to a particular project, department, or domain. An organization can have multiple datasets and users can have different roles within the organization.

## Creating an Organization

To create a new organization, you need to send a POST request with the organization's details.

```python
import requests

base_url = "http://127.0.0.1:8000"

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
```

## Registering a Data Source

Once the organization is created, you can register a new dataset under it.

```python
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
```

## Searching for Data Sources

You can search for datasets by different criteria. Below are a few examples:

### Search by Dataset Name

```python
dataset_name = input("Enter the dataset name to search for: ")
response = requests.get(f"{base_url}/datasource", params={"dataset_name": dataset_name})

if response.status_code == 200:
    results = response.json()
    print(f"Datasets found: {results}")
else:
    print(f"Error: {response.json()['detail']}")
```

### Search by Organization Name

```python
response = requests.get(f"{base_url}/datasource", params={"owner_org": organization_name})

if response.status_code == 200:
    results = response.json()
    print(f"Datasets found: {results}")
else:
    print(f"Error: {response.json()['detail']}")
```

### Search by Term

```python
search_term = input("Enter the search term: ")
response = requests.get(f"{base_url}/datasource", params={"search_term": search_term})

if response.status_code == 200:
    results = response.json()
    print(f"Datasets found: {results}")
else:
    print(f"Error: {response.json()['detail']}")
```

## Listing All Organizations

You can list all organizations available in the CKAN instance.

```python
response = requests.get(f"{base_url}/organization")

if response.status_code == 200:
    organizations = response.json()
    print(f"Organizations: {organizations}")
else:
    print(f"Error: {response.json()['detail']}")
```

## Deleting an Organization

To delete an organization and all its datasets, send a DELETE request with the organization's name.

```python
response = requests.delete(f"{base_url}/organization/{organization_name}")

if response.status_code == 200:
    print(f"Organization deleted successfully.")
else:
    print(f"Error: {response.json()['detail']}")
```

You can find the complete Python script that follows this tutorial [here](api_with_requests.py).

Return to [README](../README.md).
