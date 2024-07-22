from fastapi import APIRouter, HTTPException, status, Depends, Body
from api.services.streaming_services.stream_manager import create_stream
from api.models.request_stream_model import ProducerPayload
from typing import Dict, Any
from api.services.keycloak_services.get_current_user import get_current_user

router = APIRouter()

@router.post(
    "/stream",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Kafka stream",
    description="Create a new Kafka stream with the filtered and standardized data.",
    responses={
        201: {
            "description": "Stream created successfully",
            "content": {
                "application/json": {
                    "example": {"topic": "stream_topic"}
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Error creating stream: <error message>"}
                }
            }
        }
    }
)
async def create_kafka_stream(
    payload: ProducerPayload = Body(...),
    _: Dict[str, Any] = Depends(get_current_user)
):
    try:
        data_stream_id = await create_stream(payload)
        return {"topic": f"data_stream_{data_stream_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
