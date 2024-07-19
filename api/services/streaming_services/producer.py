import logging
from concurrent.futures import ThreadPoolExecutor
import asyncio
from uuid import uuid4
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaTimeoutError
from tenacity import retry, stop_after_attempt, wait_fixed
import pandas as pd
import json
from api.config.kafka_settings import kafka_settings
from .compressor import compress_data

KAFKA_SERVER = f"{kafka_settings.kafka_host}:{kafka_settings.kafka_port}"

logger = logging.getLogger(__name__)

CHUNK_SIZE = 10000
TIME_WINDOW = 10  # seconds

class Producer:
    def __init__(self, filter_semantics, data_streams):
        self.data_stream_id = str(uuid4())
        self.data_streams = [stream for stream in data_streams if stream.extras.get('mapping')]
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
            tasks = [self.process_stream(stream) for stream in self.data_streams]
            await asyncio.gather(*tasks)
        finally:
            await self.producer.stop()
            logger.info(f"Producer stopped for data stream ID: {self.data_stream_id}")

    async def process_stream(self, stream):
        resource = stream.resources[0]
        if resource.format == 'kafka':
            await self.process_kafka_stream(stream, stream.extras)
        else:
            logger.info(f"Unsupported stream format: {resource.format}")

    async def process_kafka_stream(self, stream, extras):
        kafka_host = extras['host']
        kafka_port = extras['port']
        kafka_topic = extras['topic']
        mapping = extras['mapping']
        logger.info(f"Processing Kafka stream: {kafka_topic} from {kafka_host}:{kafka_port} with mapping {mapping}")

        consumer = AIOKafkaConsumer(
            kafka_topic,
            bootstrap_servers=f"{kafka_host}:{kafka_port}",
            auto_offset_reset='earliest'
        )
        await consumer.start()
        try:
            start_time = self.loop.time()
            messages = []

            async for message in consumer:
                data = json.loads(message.value)
                mapped_data = {key: self.extract_value(data, path) for key, path in mapping.items()}
                filtered_data = self.apply_filters(mapped_data)
                messages.append(filtered_data)

                elapsed_time = self.loop.time() - start_time
                if elapsed_time >= TIME_WINDOW or len(messages) >= CHUNK_SIZE:
                    await self.send_data(messages, stream)
                    messages = []
                    start_time = self.loop.time()
        finally:
            await consumer.stop()
            logger.info(f"Consumer stopped for Kafka stream: {kafka_topic}")

    async def send_data(self, messages, stream):
        data_structure = {"values": {}, "stream_info": stream.extras}
        for message in messages:
            for key, value in message.items():
                if key not in data_structure["values"]:
                    data_structure["values"][key] = []
                data_structure["values"][key].append(value)

        compressed_data = compress_data(data_structure)
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

    async def stop_producer(self):
        await self.producer.stop()
        logger.info(f"Producer stopped for data stream ID: {self.data_stream_id}")

    async def stop(self):
        self.stop_event.set()
        await self.stop_producer()
