import random
import string
import requests
import pytest
import time

# Constants
API_URL = "http://localhost:8000"
KAFKA_HOST = '155.101.6.194'
KAFKA_PORT = '9092'
KAFKA_TOPIC_PREFIX = 'random_topic_example_'
OWNER_ORG = "test_org1"
USERNAME = "placeholder@placeholder.com"
PASSWORD = "placeholder"

# Function to generate a unique Kafka topic name
def generate_unique_kafka_topic():
    return KAFKA_TOPIC_PREFIX + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

# Function to get auth token
def get_auth_token(api_url, username, password):
    endpoint = f"{api_url}/token"
    response = requests.post(endpoint, data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to retrieve auth token. Status code: {response.status_code}, Response: {response.text}")
        response.raise_for_status()

# Function to post Kafka dataset data to CKAN
def post_kafka_datasource(api_url, dataset_data, headers):
    endpoint = f"{api_url}/kafka"
    response = requests.post(endpoint, json=dataset_data, headers=headers)

    if response.status_code == 201:
        print("Dataset created successfully:", response.json())
        return response.json()
    else:
        print("Error creating dataset:", response.status_code, response.json())
        response.raise_for_status()

# Function to get Kafka datasets from CKAN
def get_kafka_datasets(api_url, headers):
    endpoint = f"{api_url}/kafka"
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        datasets = response.json()
        kafka_datasets = [ds for ds in datasets if ds['resources'] and any(res['description'].startswith("Kafka topic") for res in ds['resources'])]
        return kafka_datasets
    else:
        print(f"Failed to retrieve datasets. Status code: {response.status_code}, Response: {response.text}")
        response.raise_for_status()

# Function to update Kafka dataset data in CKAN
def put_kafka_datasource(api_url, dataset_id, update_data, headers):
    endpoint = f"{api_url}/kafka/{dataset_id}"
    response = requests.put(endpoint, json=update_data, headers=headers)

    if response.status_code == 200:
        print("Dataset updated successfully:", response.json())
        return response.json()
    else:
        print("Error updating dataset:", response.status_code, response.json())
        response.raise_for_status()

# Function to delete Kafka dataset from CKAN
def delete_kafka_datasource(api_url, dataset_id, headers):
    endpoint = f"{api_url}/kafka/{dataset_id}"
    response = requests.delete(endpoint, headers=headers)

    if response.status_code == 200:
        print("Dataset deleted successfully:", response.json())
        return response.json()
    else:
        print("Error deleting dataset:", response.status_code, response.json())
        response.raise_for_status()

# Pytest test function
@pytest.mark.asyncio
async def test_kafka_ckan_integration():
    # Get auth token
    token = get_auth_token(API_URL, USERNAME, PASSWORD)
    headers = {"Authorization": f"Bearer {token}"}

    # Generate a unique Kafka topic name
    kafka_topic = generate_unique_kafka_topic()

    # Step 2: Register Kafka topic as dataset in CKAN
    dataset_data = {
        "dataset_name": kafka_topic,
        "dataset_title": "Random Topic Example",
        "owner_org": OWNER_ORG,
        "kafka_topic": kafka_topic,
        "kafka_host": KAFKA_HOST,
        "kafka_port": KAFKA_PORT,
        "dataset_description": "This is a randomly generated Kafka topic registered as a CKAN dataset."
    }
    created_dataset = post_kafka_datasource(API_URL, dataset_data, headers)
    dataset_id = created_dataset["id"]

    # Add a delay to ensure the dataset is indexed
    time.sleep(2)

    # Step 3: Retrieve Kafka dataset information from CKAN
    kafka_datasets = get_kafka_datasets(API_URL, headers)
    dataset_info = next((ds for ds in kafka_datasets if ds['name'] == kafka_topic), None)
    assert dataset_info is not None

    # Step 4: Update Kafka dataset
    update_data = {
        "dataset_title": "Updated Random Topic Example",
        "dataset_description": "This is an updated description.",
        "extras": {"new_key": "new_value"}
    }
    put_kafka_datasource(API_URL, dataset_id, update_data, headers)

    # Add a delay to ensure the dataset is updated
    time.sleep(2)

    # Step 5: Verify the update
    updated_datasets = get_kafka_datasets(API_URL, headers)
    updated_dataset_info = next((ds for ds in updated_datasets if ds['name'] == kafka_topic), None)
    assert updated_dataset_info is not None
    assert updated_dataset_info["title"] == "Updated Random Topic Example"
    assert updated_dataset_info["notes"] == "This is an updated description."
    assert "new_key" in updated_dataset_info["extras"]
    assert updated_dataset_info["extras"]["new_key"] == "new_value"

    # Step 6: Delete Kafka dataset
    delete_kafka_datasource(API_URL, dataset_id, headers)

    # Add a delay to ensure the dataset is deleted
    time.sleep(2)

    # Step 7: Verify the deletion
    deleted_datasets = get_kafka_datasets(API_URL, headers)
    deleted_dataset_info = next((ds for ds in deleted_datasets if ds['name'] == kafka_topic), None)
    assert deleted_dataset_info is None

if __name__ == "__main__":
    pytest.main([__file__])
