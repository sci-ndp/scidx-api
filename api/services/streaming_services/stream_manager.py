import logging
import asyncio
import json
import signal
from fastapi import HTTPException
from api.models.request_stream_model import ProducerPayload
from .consumer import consume_kafka_data, active_consumers
from .producer import Producer, active_producers, delete_all_created_streams, kafka_settings
from api.services.datasource_services import search_datasource


logger = logging.getLogger(__name__)


async def create_stream(payload: ProducerPayload):
    logger.info("Searching data sources with keywords: %s", payload.keywords)

    # Normalize and split keywords into a list
    if payload.keywords:
        keywords_list = [keyword.strip().lower() for keyword in payload.keywords.split(',')]
    else:
        keywords_list = []

    # Perform the search based on the match_all flag
    filtered_streams = await search_datasource_based_on_keywords(keywords_list, payload.match_all)
    
    logger.info("Total streams found after filtering: %d", len(filtered_streams))

    if not filtered_streams:
        raise HTTPException(status_code=404, detail="No data streams found matching the criteria.")

    # Create a new Producer and start it asynchronously
    producer = Producer(payload.filter_semantics, filtered_streams)
    active_producers.append(producer)
    
    asyncio.create_task(safe_producer_run(producer))

    logger.info("Stream created with ID: %s", producer.data_stream_id)
    involved_stream_ids = [stream.id for stream in filtered_streams]

    return producer.data_stream_id, involved_stream_ids


async def search_datasource_based_on_keywords(keywords_list, match_all):
    """
    Perform a search of data sources based on provided keywords and match_all flag.
    """
    if match_all and keywords_list:
        combined_keywords = ",".join(keywords_list)
        filtered_streams = await search_datasource(search_term=combined_keywords)
    elif keywords_list:
        filtered_streams = []
        for keyword in keywords_list:
            streams = await search_datasource(search_term=keyword)
            filtered_streams.extend(streams)
        filtered_streams = list({stream.id: stream for stream in filtered_streams}.values())  # Remove duplicates
    else:
        filtered_streams = await search_datasource()
    
    return filtered_streams


def stream_matches_keywords(stream, keywords_list, match_all):
    """
    Check if the stream's attributes match any or all of the provided keywords.
    """
    stream_str = json.dumps(stream.__dict__, default=str).lower()
    if match_all:
        return all(keyword in stream_str for keyword in keywords_list)
    return any(keyword in stream_str for keyword in keywords_list)


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
        active_producers.remove(producer)


async def get_stream_data(topic: str):
    """
    This function consumes Kafka stream data and yields it for clients.
    """
    async for data in consume_kafka_data(topic):
        yield data


# Signal handler to gracefully handle shutdown signals like SIGINT and SIGTERM
def handle_shutdown_signal(signal_received, frame):
    logger.info(f"Signal {signal_received} received, initiating graceful shutdown...")
    asyncio.get_event_loop().call_soon(asyncio.create_task, shutdown_all_producers())

# Stop all active consumers
async def stop_all_active_consumers():
    logger.info("Shutting down all active consumers...")
    for consumer in active_consumers:
        await consumer.stop()  # Stop each consumer asynchronously
    logger.info("All consumers stopped.")

# Stop all active producers and consumers
async def shutdown_all_producers():
    logger.info("Initiating shutdown process for all producers and consumers...")

    # Stop consumers first
    await stop_all_active_consumers()

    logger.info("Shutting down all active producers...")
    for producer in active_producers:
        await producer.stop()  # Stop each producer asynchronously

    # Ensure all producers have stopped and tasks are canceled
    await asyncio.sleep(4)  # Delay to ensure all tasks are properly completed
    logger.info("All producers stopped.")

    # Finally delete all created data streams
    await delete_all_created_streams()
