import logging
from concurrent.futures import ThreadPoolExecutor
import asyncio
from uuid import uuid4
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from .compressor import compress_data
from api.config.kafka_settings import kafka_settings

KAFKA_SERVER = f"{kafka_settings.kafka_host}:{kafka_settings.kafka_port}"

logger = logging.getLogger(__name__)

class Producer:
    def __init__(self, filter_semantics, data_streams):
        self.data_stream_id = str(uuid4())
        self.data_streams = data_streams
        self.filter_semantics = filter_semantics
        self.stop_event = asyncio.Event()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.loop = asyncio.get_running_loop()
        self.producer = AIOKafkaProducer(bootstrap_servers=KAFKA_SERVER)
        logger.info(f"Producer initialized with ID: {self.data_stream_id}")

    async def run(self):
        await self.producer.start()
        logger.info(f"Producer started for data stream ID: {self.data_stream_id}")
        try:
            tasks = [self.process_kafka_stream(stream) for stream in self.data_streams]
            await asyncio.gather(*tasks)
        finally:
            await self.producer.stop()
            logger.info(f"Producer stopped for data stream ID: {self.data_stream_id}")

    async def process_kafka_stream(self, stream):
        kafka_host = stream.extras['host']
        kafka_port = stream.extras['port']
        kafka_topic = stream.extras['topic']
        mapping = stream.extras['mapping']
        logger.info(f"Processing Kafka stream: {kafka_topic} from {kafka_host}:{kafka_port} with mapping {mapping}")

        consumer = AIOKafkaConsumer(
            kafka_topic,
            bootstrap_servers=f"{kafka_host}:{kafka_port}",
            auto_offset_reset='earliest'
        )
        await consumer.start()
        try:
            async for message in consumer:
                data = json.loads(message.value)
                mapped_data = {key: self.extract_value(data, path) for key, path in mapping.items()}
                filtered_data = self.apply_filters(mapped_data)
                await self.send_data(filtered_data)
        finally:
            await consumer.stop()
            logger.info(f"Consumer stopped for Kafka stream: {kafka_topic}")

    async def send_data(self, data):
        compressed_data = compress_data(data)
        await self.producer.send_and_wait(f"data_stream_{self.data_stream_id}", compressed_data)

    def extract_value(self, data, path):
        keys = path.split('.')
        for key in keys:
            data = data.get(key)
            if data is None:
                return None
        return data

    def apply_filters(self, data):
        # Apply your filter semantics here if necessary
        return data
