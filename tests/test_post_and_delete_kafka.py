from fastapi.testclient import TestClient
from api.main import app
from api.config import keycloak_settings
import random
import string

client = TestClient(app)

def generate_random_name(prefix="test"):
    return f"{prefix}_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def test_create_and_delete_kafka_resource_with_org():
    org_name = generate_random_name("org")
    dataset_name = generate_random_name("kafka_dataset")
    resource_name = generate_random_name("kafka_resource")
    
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

    # Step 2: Create the Kafka dataset under the new organization
    kafka_payload = {
        "dataset_name": dataset_name,
        "dataset_title": "Kafka Dataset Test",
        "owner_org": org_name,
        "kafka_topic": resource_name,
        "kafka_host": "localhost",
        "kafka_port": "9092",
        "dataset_description": "This is a test Kafka dataset.",
        "extras": {
            "key1": "value1",
            "key2": "value2"
        },
        "mapping": {
            "field1": "mapping1",
            "field2": "mapping2"
        },
        "processing": {
            "data_key": "data",
            "info_key": "info"
        }
    }

    create_kafka_response = client.post("/kafka", json=kafka_payload, headers=headers)
    assert create_kafka_response.status_code == 201

    create_kafka_data = create_kafka_response.json()
    assert "id" in create_kafka_data

    # Verify the ID of the created dataset
    dataset_id = create_kafka_data["id"]
    print(f"Dataset created with ID: {dataset_id}")

    # Step 3: Delete the Kafka resource
    delete_response = client.delete(f"/resource/{dataset_name}", headers=headers)
    
    # Print the error detail if the deletion fails
    if delete_response.status_code != 200:
        print(f"Error deleting resource: {delete_response.json()}")
    
    assert delete_response.status_code == 200
    
    delete_data = delete_response.json()
    assert "deleted successfully" in delete_data["message"]

    # Step 4: Delete the organization
    delete_org_response = client.delete(f"/organization/{org_name}", headers=headers)
    assert delete_org_response.status_code == 200
    
    delete_org_data = delete_org_response.json()
    assert delete_org_data["message"] == "Organization deleted successfully"
