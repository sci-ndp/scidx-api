from fastapi import APIRouter, HTTPException, status, Depends
from api.services import kafka_services
from api.models.request_kafka_model import KafkaDataSourceUpdateRequest
from tenacity import RetryError
from typing import Dict, Any

from api.services.keycloak_services.get_current_user import get_current_user

router = APIRouter()

@router.put(
    "/kafka/{dataset_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update a Kafka topic",
    description="Update a Kafka topic and its associated metadata in the system.",
    responses={
        200: {
            "description": "Kafka dataset updated successfully",
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
                    "example": {"detail": "Error updating Kafka dataset: <error message>"}
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
    """
    Update a Kafka topic and its associated metadata in the system.

    Parameters
    ----------
    dataset_id : str
        The ID of the dataset to be updated.
    data : KafkaDataSourceUpdateRequest
        An object containing all the required parameters for updating a Kafka dataset and resource.

    Returns
    -------
    dict
        A dictionary containing the ID of the updated dataset if successful.

    Raises
    ------
    HTTPException
        If there is an error updating the dataset or resource, an HTTPException is raised with a detailed message.
    """
    try:
        dataset_id = kafka_services.update_kafka(
            dataset_id=dataset_id,
            dataset_name=data.dataset_name,
            dataset_title=data.dataset_title,
            owner_org=data.owner_org,
            kafka_topic=data.kafka_topic,
            kafka_host=data.kafka_host,
            kafka_port=data.kafka_port,
            dataset_description=data.dataset_description,
            extras=data.extras
        )
        return {"id": dataset_id}
    except RetryError as e:
        final_exception = e.last_attempt.exception()
        raise HTTPException(status_code=400, detail=str(final_exception))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
