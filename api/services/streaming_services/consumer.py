import logging
import json
from aiokafka import AIOKafkaConsumer
from api.config.kafka_settings import kafka_settings
from .compressor import decompress_data

KAFKA_SERVER = f"{kafka_settings.kafka_host}:{kafka_settings.kafka_port}"
logger = logging.getLogger(__name__)

async def consume_kafka_data(topic: str):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_SERVER,
        auto_offset_reset='earliest'
    )
    await consumer.start()
    logger.info(f"Consumer started for topic: {topic}")
    try:
        async for message in consumer:
            decompressed_message = decompress_data(message.value)
            yield f"{json.dumps(decompressed_message)}\n"
    finally:
        await consumer.stop()
        logger.info(f"Consumer stopped for topic: {topic}")
