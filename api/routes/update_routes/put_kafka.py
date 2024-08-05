
from fastapi import APIRouter, HTTPException, status, Depends
from api.services import kafka_services
from api.models.update_kafka_model import KafkaDataSourceUpdateRequest
from typing import Dict, Any

from api.services.keycloak_services.get_current_user import get_current_user

router = APIRouter()

@router.put(
    "/kafka/{dataset_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update an existing Kafka topic",
    description="""
Update an existing Kafka topic and its associated metadata.

### Optional Fields
- **dataset_name**: The unique name of the dataset to be updated.
- **dataset_title**: The title of the dataset to be updated.
- **owner_org**: The ID of the organization to which the dataset belongs.
- **kafka_topic**: The Kafka topic name.
- **kafka_host**: The Kafka host.
- **kafka_port**: The Kafka port.
- **dataset_description**: A description of the dataset.
- **extras**: Additional metadata to be updated or added to the dataset.
- **mapping**: Mapping information for the dataset.
- **processing**: Processing information for the dataset.

### Example Payload
```json
{
    "dataset_name": "kafka_topic_example_updated",
    "kafka_topic": "example_topic_updated"
}
```
""",
    responses={
        200: {
            "description": "Kafka dataset updated successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Kafka dataset updated successfully"}
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Error updating Kafka dataset: <error message>"}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Kafka dataset not found"}
                }
            }
        }
    }
)
async def update_kafka_datasource(
    dataset_id: str,
    data: KafkaDataSourceUpdateRequest,
    _: Dict[str, Any] = Depends(get_current_user)
):
    try:
        updated = kafka_services.update_kafka(
            dataset_id=dataset_id,
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
        if not updated:
            raise HTTPException(status_code=404, detail="Kafka dataset not found")
        return {"message": "Kafka dataset updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
