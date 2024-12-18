import json
from aiokafka import AIOKafkaConsumer
import asyncio
import logging
import time

from api.services.streaming_services.data_cleaning import process_and_send_data

logger = logging.getLogger(__name__)

CHUNK_SIZE = 10000
TIME_WINDOW = 10  # seconds

async def process_kafka_stream(stream, filter_semantics, buffer_lock, send_data, loop, stop_event):
    kafka_host = stream.extras['host']
    kafka_port = stream.extras['port']
    kafka_topic = stream.extras['topic']
    mapping = stream.extras.get('mapping', None)
    processing = stream.extras.get('processing', {})
    data_key = processing.get('data_key', None)
    info_key = processing.get('info_key', None)

    logger.info(f"Processing Kafka stream: {kafka_topic} from {kafka_host}:{kafka_port} with mapping {mapping}")

    consumer = AIOKafkaConsumer(
        kafka_topic,
        bootstrap_servers=f"{kafka_host}:{kafka_port}",
        auto_offset_reset='earliest',
        group_id=f"group_{kafka_topic}_{int(time.time())}"  # Unique group ID to avoid offset issues
    )
    await consumer.start()

    try:
        start_time = loop.time()
        last_send_time = time.time()
        messages = []
        additional_info = None
        timeout_counter = 0

        while not stop_event.is_set():  # Stop event to handle graceful shutdown
            try:
                # Fetch message with a timeout to prevent blocking
                message = await asyncio.wait_for(consumer.getone(), timeout=TIME_WINDOW)
                data = json.loads(message.value)
                
                if info_key:
                    additional_info = data.get(info_key, {})

                if data_key:
                    data = data.get(data_key, {})
                
                messages.append(data)

                # Reset timeout counter when a message is received
                timeout_counter = 0

            except asyncio.TimeoutError:
                logger.info("No new messages received in TIME_WINDOW")
                timeout_counter += 1

            # If no new messages after multiple timeouts, stop the stream
            if timeout_counter >= 3:
                logger.info(f"No new messages received for {6 * TIME_WINDOW} seconds. Stopping the stream.")
                break

            # Send data after a chunk or time window is met
            if len(messages) >= CHUNK_SIZE or time.time() - last_send_time >= TIME_WINDOW:
                await process_and_send_data(messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics, additional_info)
                messages.clear()
                last_send_time = time.time()

        # Send any remaining messages before shutdown
        if messages:
            await process_and_send_data(messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics, additional_info)

    except Exception as e:
        logger.error(f"Error in Kafka stream processing: {e}")
    finally:
        logger.info(f"Shutting down Kafka consumer for topic: {kafka_topic}")
        try:
            await consumer.stop()  # Ensure the consumer stops properly
        except Exception as shutdown_error:
            logger.error(f"Error shutting down Kafka consumer: {shutdown_error}")
        logger.info(f"Kafka consumer for topic: {kafka_topic} has been shut down.")
