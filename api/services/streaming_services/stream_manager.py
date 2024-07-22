import logging
import asyncio

from api.models.request_stream_model import ProducerPayload
from .consumer import consume_kafka_data
from .producer import Producer
from api.services.datasource_services import search_datasource

logger = logging.getLogger(__name__)

async def create_stream(payload: ProducerPayload):
    logger.info("Searching data sources with keywords: %s", payload.keywords)
    filtered_streams = await search_datasource(search_term=payload.keywords)

    logger.info("Total streams found: %d", len(filtered_streams))
    logger.info("Streams: %s", filtered_streams)

    filtered_streams = [stream for stream in filtered_streams if stream.extras.get('mapping')]

    logger.info("Total streams after filtering: %d", len(filtered_streams))
    logger.info("Filtered Streams: %s", filtered_streams)

    if not filtered_streams:
        raise ValueError("No data streams found matching the criteria.")

    producer = Producer(payload.filter_semantics, filtered_streams)
    asyncio.create_task(producer.run())
    logger.info("Stream created with ID: %s", producer.data_stream_id)
    return producer.data_stream_id

async def get_stream_data(topic: str):
    async for data in consume_kafka_data(topic):
        yield data
