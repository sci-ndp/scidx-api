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

    # Split the keywords string into a list of individual keywords
    if payload.keywords:
        keywords_list = [keyword.strip() for keyword in payload.keywords.split(',')]
    else:
        keywords_list = []

    filtered_streams = await search_datasource(search_term=payload.keywords)

    logger.info("Total streams found: %d", len(filtered_streams))
    logger.info("Streams: %s", filtered_streams)

    def stream_matches_keywords(stream, keywords_list):
        """
        Convert the stream object to a JSON string and check if any/all of the keywords are present.
        """
        stream_str = json.dumps(stream.__dict__, default=str).lower()  # Convert stream object to JSON string

        if payload.match_all:
            return all(keyword.lower() in stream_str for keyword in keywords_list)
        else:
            return any(keyword.lower() in stream_str for keyword in keywords_list)

    # Filter streams based on the updated logic
    filtered_streams = [
        stream for stream in filtered_streams
        if stream_matches_keywords(stream, keywords_list)
    ]

    logger.info("Total streams after filtering: %d", len(filtered_streams))
    logger.info("Filtered Streams: %s", filtered_streams)

    if not filtered_streams:
        raise HTTPException(status_code=404, detail="No data streams found matching the criteria.")

    producer = Producer(payload.filter_semantics, filtered_streams)
    asyncio.create_task(producer.run())
    logger.info("Stream created with ID: %s", producer.data_stream_id)
    return producer.data_stream_id

async def get_stream_data(topic: str):
    async for data in consume_kafka_data(topic):
        yield data
