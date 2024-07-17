import asyncio
import json
from aiokafka import AIOKafkaConsumer
from api.config.kafka_settings import kafka_settings
from .compressor import decompress_data

KAFKA_SERVER = f"{kafka_settings.kafka_host}:{kafka_settings.kafka_port}"

async def consume_kafka_data(topic: str):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_SERVER,
        group_id=topic,
        auto_offset_reset='earliest'
    )
    await consumer.start()
    try:
        async for message in consumer:
            decompressed = decompress_data(message.value)
            yield json.dumps(decompressed)
    finally:
        await consumer.stop()
