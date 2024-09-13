import logging
import asyncio
import json

from fastapi import HTTPException
from api.models.request_stream_model import ProducerPayload
from .consumer import consume_kafka_data
from .producer import Producer
from api.services.datasource_services import search_datasource

logger = logging.getLogger(__name__)

async def create_stream(payload: ProducerPayload):
    logger.info("Searching data sources with keywords: %s", payload.keywords)

    # Split keywords string into a list of individual keywords
    if payload.keywords:
        keywords_list = [keyword.strip().lower() for keyword in payload.keywords.split(',')]
    else:
        keywords_list = []

    # Fetch all possible streams based on search terms
    filtered_streams = await search_datasource(search_term=payload.keywords)

    logger.info("Total streams found: %d", len(filtered_streams))

    def stream_matches_keywords(stream, keywords_list):
        """
        Check if the stream's attributes match any or all of the provided keywords.
        Convert the stream object to a JSON string, then search for keywords.
        """
        # Convert stream object to JSON string in lowercase for easier keyword matching
        stream_str = json.dumps(stream.__dict__, default=str).lower()

        if payload.match_all:
            return all(keyword in stream_str for keyword in keywords_list)
        else:
            return any(keyword in stream_str for keyword in keywords_list)

    # Filter streams based on keywords
    if keywords_list:
        filtered_streams = [stream for stream in filtered_streams if stream_matches_keywords(stream, keywords_list)]
    
    logger.info("Total streams after filtering: %d", len(filtered_streams))

    if not filtered_streams:
        raise HTTPException(status_code=404, detail="No data streams found matching the criteria.")

    # Create a new Producer and start it asynchronously
    producer = Producer(payload.filter_semantics, filtered_streams)
    
    # Ensure we catch any errors from the task and handle them properly
    asyncio.create_task(safe_producer_run(producer))
    
    logger.info("Stream created with ID: %s", producer.data_stream_id)
    return producer.data_stream_id


async def safe_producer_run(producer):
    """
    Ensure the producer runs safely and handles any errors or exceptions gracefully.
    """
    try:
        await producer.run()
    except Exception as e:
        logger.error(f"Producer encountered an error: {e}")
    finally:
        logger.info(f"Producer {producer.data_stream_id} has stopped.")

async def get_stream_data(topic: str):
    """
    This function consumes Kafka stream data and yields it for clients.
    """
    async for data in consume_kafka_data(topic):
        yield data
