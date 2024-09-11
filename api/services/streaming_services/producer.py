import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
from aiokafka import AIOKafkaProducer
from api.config.kafka_settings import kafka_settings
from .compressor import compress_data
from .stream_processing.kafka import process_kafka_stream
from .stream_processing.url import process_url_stream

KAFKA_SERVER = f"{kafka_settings.kafka_host}:{kafka_settings.kafka_port}"

logger = logging.getLogger(__name__)

class Producer:
    def __init__(self, filter_semantics, data_streams):
        self.data_stream_id = str(uuid4())
        self.data_streams = data_streams
        self.filter_semantics = filter_semantics
        self.stop_event = asyncio.Event()
        self.executor = ThreadPoolExecutor(max_workers=10)  # Control I/O-bound task concurrency
        self.loop = asyncio.get_running_loop()
        self.producer = AIOKafkaProducer(bootstrap_servers=KAFKA_SERVER)
        self.buffer_lock = asyncio.Lock()
        self.tasks = []
        self.retry_limit = 5
        self.retry_attempts = {}
        logger.info(f"Producer initialized with ID: {self.data_stream_id}")

    async def run(self):
        """Start the Kafka producer and begin streaming data from all streams."""
        await self.producer.start()
        logger.info(f"Producer started for data stream ID: {self.data_stream_id}")
        try:
            # Launch tasks for each stream
            self.tasks = [asyncio.create_task(self.process_stream(stream)) for stream in self.data_streams]
            await asyncio.gather(*self.tasks)
        except Exception as e:
            logger.error(f"Exception in Producer: {e}")
        finally:
            await self.shutdown_producer()

    async def process_stream(self, stream):
        """Process a single stream based on its type (Kafka or URL)."""
        resource = stream.resources[0]
        try:
            if resource.format == 'kafka':
                await process_kafka_stream(
                    stream,
                    self.filter_semantics,
                    self.buffer_lock,
                    self.send_data,
                    self.loop
                )
            elif resource.format == 'url':
                stop_event = asyncio.Event()  
                await process_url_stream(
                    stream,
                    self.filter_semantics,
                    self.buffer_lock,
                    self.send_data,
                    self.loop,
                    stop_event
                )
            else:
                logger.warning(f"Unsupported stream format: {resource.format}")
        except Exception as e:
            await self.handle_stream_error(stream, e)

    async def handle_stream_error(self, stream, error):
        """Handle errors during stream processing with retry logic."""
        resource = stream.resources[0]
        logger.error(f"Error processing stream {resource.format}: {error}")
        # Retry logic with exponential backoff
        retries = self.retry_attempts.get(stream, 0)
        if retries < self.retry_limit:
            self.retry_attempts[stream] = retries + 1
            backoff_time = 2 ** retries  # Exponential backoff
            logger.info(f"Retrying stream {resource.format} in {backoff_time} seconds...")
            await asyncio.sleep(backoff_time)
            await self.process_stream(stream)  # Retry the stream
        else:
            logger.error(f"Retry limit reached for {resource.format}, skipping further retries.")

    async def send_data(self, df, stream, loop):
        """Send data to Kafka in compressed format."""
        data_structure = {"values": {}, "stream_info": stream.extras}
        for col in df.columns:
            data_structure["values"][col] = df[col].tolist()

        compressed_data = compress_data(data_structure)
        await self.producer.send_and_wait(f"data_stream_{self.data_stream_id}", compressed_data)

    async def stop(self):
        """Stop the producer and cancel all ongoing tasks."""
        logger.info("Stopping all producer tasks...")
        self.stop_event.set()  # Signal to stop all tasks
        
        # Cancel any running tasks gracefully
        for task in self.tasks:
            task.cancel()

        # Wait for all tasks to be canceled or finished
        await asyncio.gather(*self.tasks, return_exceptions=True)
        await self.shutdown_producer()
        
    async def shutdown_producer(self):
        """Shutdown Kafka producer and thread pool."""
        await self.producer.stop()
        self.executor.shutdown(wait=False)
        logger.info(f"Producer stopped for data stream ID: {self.data_stream_id}")
