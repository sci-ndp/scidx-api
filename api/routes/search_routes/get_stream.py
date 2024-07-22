from fastapi import APIRouter, HTTPException, Query
from typing import List
from api.services.streaming_services.consumer import consume_kafka_data
from api.config.kafka_settings import kafka_settings
import logging
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "/stream",
    response_model=List[dict],
    summary="Get Kafka stream data",
    description="Retrieve data from a Kafka stream.",
    responses={
        200: {
            "description": "Stream data retrieved successfully",
            "content": {
                "application/json": {
                    "example": [{"key": "value"}]
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Error retrieving stream data: <error message>"}
                }
            }
        }
    }
)
async def get_kafka_stream(
    topic: str = Query(..., description="The Kafka topic to retrieve data from.")
):
    try:
        return StreamingResponse(consume_kafka_data(topic), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Error retrieving stream data: {e}")
        raise HTTPException(status_code=400, detail=str(e))
