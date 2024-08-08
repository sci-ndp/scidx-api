import logging
import json
from typing import Optional
from aiokafka import AIOKafkaConsumer
from api.config.kafka_settings import kafka_settings
from .compressor import decompress_data

KAFKA_SERVER = f"{kafka_settings.kafka_host}:{kafka_settings.kafka_port}"
logger = logging.getLogger(__name__)

async def consume_kafka_data(topic: str, host: Optional[str] = None, port: Optional[int] = None, use_compression: bool = True):
    kafka_server = f"{host}:{port}" if host and port else KAFKA_SERVER
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=kafka_server,
        auto_offset_reset='earliest'
    )
    await consumer.start()
    logger.info(f"Consumer started for topic: {topic} on {kafka_server}")
    try:
        async for message in consumer:
            if use_compression:
                decompressed_message = decompress_data(message.value)
                yield f"{json.dumps(decompressed_message)}\n"
            else:
                yield f"{json.dumps(message.value.decode())}\n"
    finally:
        await consumer.stop()
        logger.info(f"Consumer stopped for topic: {topic}")
