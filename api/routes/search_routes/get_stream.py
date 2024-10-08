from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from api.services.streaming_services.consumer import consume_kafka_data
from api.config.ckan_settings import ckan_settings
from api.config.kafka_settings import kafka_settings

import logging
from fastapi.responses import StreamingResponse
import requests
import asyncio

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
    id: Optional[str] = Query(None, description="The ID of the dataset to retrieve."),
    topic: Optional[str] = Query(None, description="The Kafka topic to retrieve data from."),
    host: Optional[str] = Query(None, description="The Kafka host to connect to."),
    port: Optional[int] = Query(None, description="The Kafka port to connect to.")
):
    try:
        if id:
            # Fetch the entry from CKAN based on the provided ID
            ckan_url = f"{ckan_settings.ckan_url}api/3/action/package_show?id={id}"
            response = requests.get(ckan_url)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to retrieve CKAN dataset.")

            ckan_data = response.json()
            resources = ckan_data.get("result", {}).get("resources", [])
            kafka_resource = next((res for res in resources if res.get("format") == "kafka"), None)
            
            if not kafka_resource:
                raise HTTPException(status_code=400, detail="No Kafka resource found for the provided ID.")
            
            topic = kafka_resource.get("name")
            host = kafka_resource.get("host", kafka_settings.kafka_host)
            port = kafka_resource.get("port", kafka_settings.kafka_port)

        if topic and host and port:
            # Call generator with the added logic to stop on client disconnect
            return StreamingResponse(
                kafka_event_generator(topic=topic, host=host, port=port, use_compression=False),
                media_type="text/event-stream"
            )
        elif topic:
            return StreamingResponse(
                kafka_event_generator(topic=topic),
                media_type="text/event-stream"
            )
        else:
            raise HTTPException(status_code=400, detail="Topic must be provided if ID is not specified.")
        
    except Exception as e:
        logger.error(f"Error retrieving stream data: {e}")
        raise HTTPException(status_code=400, detail=str(e))


async def kafka_event_generator(topic: str, host: Optional[str] = None, port: Optional[int] = None, use_compression: bool = True):
    consumer_generator = consume_kafka_data(topic=topic, host=host, port=port, use_compression=use_compression)
    
    try:
        # Iterate over the generator (do not use `await` here)
        async for message in consumer_generator:
            yield message
    except asyncio.CancelledError:
        logger.info(f"Client disconnected from stream: {topic}. Closing consumer.")
        await consumer_generator.aclose()  # Ensure the consumer is stopped when client disconnects
    finally:
        logger.info(f"Kafka consumer stopped for topic: {topic}.")
