import json
from aiokafka import AIOKafkaConsumer
import asyncio
import logging
import time

from api.services.streaming_services.data_cleaning import process_and_send_data

logger = logging.getLogger(__name__)

CHUNK_SIZE = 10000
TIME_WINDOW = 10  # seconds


async def process_kafka_stream(stream, filter_semantics, buffer_lock, send_data, loop):
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

        while True:
            try:
                message = await asyncio.wait_for(consumer.getone(), timeout=TIME_WINDOW)
                data = json.loads(message.value)
                
                if info_key:
                    additional_info = data.get(info_key, {})

                if data_key:
                    data = data.get(data_key, {})
                
                messages.append(data)

            except asyncio.TimeoutError:
                logger.info("No new messages received in TIME_WINDOW")

            elapsed_time = loop.time() - start_time
            time_since_last_send = time.time() - last_send_time

            # Check if it's time to send the accumulated messages
            if len(messages) >= CHUNK_SIZE or time_since_last_send >= TIME_WINDOW or elapsed_time >= TIME_WINDOW:
                await process_and_send_data(messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics, additional_info)
                messages.clear()  # Clear messages after sending
                start_time = loop.time()
                last_send_time = time.time()

            # If no more messages, break the loop
            if not messages and time_since_last_send >= TIME_WINDOW:
                break

        # Send any remaining messages
        if messages:
            await process_and_send_data(messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics, additional_info)

    except Exception as e:
        logger.error(f"Error in Kafka stream processing: {e}")

    finally:
        await consumer.stop()
