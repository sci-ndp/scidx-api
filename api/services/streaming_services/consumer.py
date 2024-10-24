# consumer.py

import logging
import json
from typing import Optional
from aiokafka import AIOKafkaConsumer
from api.config.kafka_settings import kafka_settings
from .compressor import decompress_data
from confluent_kafka.admin import AdminClient, KafkaException

KAFKA_SERVER = f"{kafka_settings.kafka_host}:{kafka_settings.kafka_port}"
logger = logging.getLogger(__name__)

active_consumers = []  # List to track active consumers

async def consume_kafka_data(topic: str, host: Optional[str] = None, port: Optional[int] = None, use_compression: bool = True):
    kafka_server = f"{host}:{port}" if host and port else KAFKA_SERVER
    
    # Check if the topic exists before starting the consumer
    if not await does_topic_exist(topic, kafka_server):
        error_msg = f"Topic '{topic}' does not exist."
        logger.error(error_msg)
        yield json.dumps({"error": error_msg})
        return  # End the generator gracefully
    
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=kafka_server,
        auto_offset_reset='earliest'
    )
    await consumer.start()
    logger.info(f"Consumer started for topic: {topic} on {kafka_server}")
    
    # Add consumer to active consumers list
    active_consumers.append(consumer)
    
    try:
        async for message in consumer:
            if use_compression:
                decompressed_message = decompress_data(message.value)
                yield f"{json.dumps(decompressed_message)}\n"
            else:
                yield f"{json.dumps(message.value.decode())}\n"
    finally:
        # Remove consumer from active consumers list and stop it
        active_consumers.remove(consumer)
        await consumer.stop()
        logger.info(f"Consumer stopped for topic: {topic}")


# Helper function to check if a Kafka topic exists
async def does_topic_exist(topic: str, kafka_server: str) -> bool:
    try:
        admin_client = AdminClient({'bootstrap.servers': kafka_server})
        metadata = admin_client.list_topics(timeout=10)
        return topic in metadata.topics
    except KafkaException as e:
        logger.error(f"Error checking Kafka topic existence: {e}")
        return False
