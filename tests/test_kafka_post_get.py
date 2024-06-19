import random
import string
import json
import requests
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import asyncio
import pytest
import time

# Constants
API_URL = "http://localhost:8000"
KAFKA_HOST = '155.101.6.194'
KAFKA_PORT = '9092'
KAFKA_TOPIC_PREFIX = 'random_topic_example_'
OWNER_ORG = "deleteme_org"

# Function to generate a unique Kafka topic name
def generate_unique_kafka_topic():
    return KAFKA_TOPIC_PREFIX + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

# Function to post Kafka dataset data to CKAN
def post_kafka_datasource(api_url, dataset_data):
    endpoint = f"{api_url}/kafka"
    response = requests.post(endpoint, json=dataset_data)

    if response.status_code == 201:
        print("Dataset created successfully:", response.json())
        return response.json()
    else:
        print("Error creating dataset:", response.status_code, response.json())
        response.raise_for_status()


# Function to get Kafka datasets from CKAN
def get_kafka_datasets(api_url):
    endpoint = f"{api_url}/datasource"
    response = requests.get(endpoint)
    if response.status_code == 200:
        datasets = response.json()
        kafka_datasets = [ds for ds in datasets if ds['resources'] and ds['resources'][0]['format'] == 'Kafka']
        return kafka_datasets
    else:
        print(f"Failed to retrieve datasets. Status code: {response.status_code}, Response: {response.text}")
        response.raise_for_status()

# Pytest test function
@pytest.mark.asyncio
async def test_kafka_ckan_integration():
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
    post_kafka_datasource(API_URL, dataset_data)

    # Add a delay to ensure the dataset is indexed
    time.sleep(2)

    # Step 3: Retrieve Kafka dataset information from CKAN
    kafka_datasets = get_kafka_datasets(API_URL)
    dataset_info = next((ds for ds in kafka_datasets if ds['name'] == kafka_topic), None)
    assert dataset_info is not None

if __name__ == "__main__":
    pytest.main([__file__])
