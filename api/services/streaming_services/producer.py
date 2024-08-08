import logging
from concurrent.futures import ThreadPoolExecutor
import asyncio
from uuid import uuid4
from aiokafka import AIOKafkaProducer
from api.config.kafka_settings import kafka_settings
from .compressor import compress_data
from .data_cleaning import process_kafka_stream

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
        self.buffer_lock = asyncio.Lock()
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
            await process_kafka_stream(
                stream,
                self.filter_semantics,
                self.buffer_lock,
                self.send_data,
                self.loop
            )
        else:
            logger.info(f"Unsupported stream format: {resource.format}")

    async def send_data(self, df, stream, loop):
        data_structure = {"values": {}, "stream_info": stream.extras}
        for col in df.columns:
            data_structure["values"][col] = df[col].tolist()

        compressed_data = compress_data(data_structure)
        await self.producer.send_and_wait(f"data_stream_{self.data_stream_id}", compressed_data)

    async def stop_producer(self):
        await self.producer.stop()
        logger.info(f"Producer stopped for data stream ID: {self.data_stream_id}")

    async def stop(self):
        self.stop_event.set()
        await self.stop_producer()
