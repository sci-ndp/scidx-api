from fastapi import APIRouter, HTTPException, status, Depends
from api.services import kafka_services
from api.models.request_kafka_model import KafkaDataSourceRequest
from tenacity import RetryError
from typing import Dict, Any

from api.services.keycloak_services.get_current_user import get_current_user

router = APIRouter()

@router.post(
    "/kafka",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new Kafka topic",
    description="""
Add a Kafka topic and its associated metadata to the system.

### Required Fields
- **dataset_name**: The unique name of the dataset to be created.
- **dataset_title**: The title of the dataset to be created.
- **owner_org**: The ID of the organization to which the dataset belongs.
- **kafka_topic**: The Kafka topic name.
- **kafka_host**: The Kafka host.
- **kafka_port**: The Kafka port.
- **dataset_description**: A description of the dataset (optional).
- **extras**: Additional metadata to be added to the dataset as extras (optional).
- **mapping**: Mapping information for the dataset. For selecting the desired fields to send and how they will be named (optional).
- **processing**: Processing information for the dataset (optional).

### Example Payload
```json
{
    "dataset_name": "kafka_topic_example",
    "dataset_title": "Kafka Topic Example",
    "owner_org": "organization_id",
    "kafka_topic": "example_topic",
    "kafka_host": "kafka_host",
    "kafka_port": "kafka_port",
    "dataset_description": "This is an example Kafka topic registered as a system dataset.",
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
```
""",
    responses={
        201: {
            "description": "Kafka dataset created successfully",
            "content": {
                "application/json": {
                    "example": {"id": "12345678-abcd-efgh-ijkl-1234567890ab"}
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Error creating Kafka dataset: <error message>"}
                }
            }
        }
    }
)
async def create_kafka_datasource(
    data: KafkaDataSourceRequest,
    _: Dict[str, Any] = Depends(get_current_user)
):
    """
    Add a Kafka topic and its associated metadata to the system.

    Parameters
    ----------
    data : KafkaDataSourceRequest
        An object containing all the required parameters for creating a Kafka dataset and resource.

    Returns
    -------
    dict
        A dictionary containing the ID of the created dataset if successful.

    Raises
    ------
    HTTPException
        If there is an error creating the dataset or resource, an HTTPException is raised with a detailed message.
    """
    try:
        dataset_id = kafka_services.add_kafka(
            dataset_name=data.dataset_name,
            dataset_title=data.dataset_title,
            owner_org=data.owner_org,
            kafka_topic=data.kafka_topic,
            kafka_host=data.kafka_host,
            kafka_port=data.kafka_port,
            dataset_description=data.dataset_description,
            extras=data.extras,
            mapping=data.mapping,
            processing=data.processing
        )
        return {"id": dataset_id}
    except RetryError as e:
        final_exception = e.last_attempt.exception()
        raise HTTPException(status_code=400, detail=str(final_exception))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
