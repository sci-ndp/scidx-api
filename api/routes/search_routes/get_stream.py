from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from api.services.streaming_services.consumer import consume_kafka_data
from api.config.kafka_settings import kafka_settings

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
        async for data in consume_kafka_data(topic):
            return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
