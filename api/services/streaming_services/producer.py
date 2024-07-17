from concurrent.futures import ThreadPoolExecutor
import asyncio
from uuid import uuid4
from typing import List
from aiokafka import AIOKafkaProducer
import aiohttp
import pandas as pd

from .compressor import compress_data, decompress_data
from api.config.kafka_settings import kafka_settings

KAFKA_SERVER = f"{kafka_settings.kafka_host}:{kafka_settings.kafka_port}"
DATA_STREAM = "data_stream"

class Producer:
    def __init__(self, filter_semantics, data_streams):
        self.data_stream_id = str(uuid4())
        self.data_streams = data_streams
        self.filter_semantics = filter_semantics
        self.stop_event = asyncio.Event()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.loop = asyncio.get_running_loop()
        self.producer = AIOKafkaProducer(bootstrap_servers=KAFKA_SERVER)

    async def run(self):
        await self.producer.start()
        async with aiohttp.ClientSession() as session:
            tasks = [self.process_stream(session, stream) for stream in self.data_streams]
            await asyncio.gather(*tasks)
        await self.producer.stop()

    async def process_stream(self, session, stream):
        async with session.get(stream.resource_url) as response:
            data = await response.json()
            # Filter data based on filter_semantics
            # Map data based on stream.extras['mapping']
            filtered_data = self.apply_filters(data)
            await self.send_data(filtered_data)

    async def send_data(self, data):
        compressed_data = compress_data(data)
        await self.producer.send_and_wait(self.data_stream_id, compressed_data)

    def apply_filters(self, data):
        # Apply your filter semantics here
        return data
