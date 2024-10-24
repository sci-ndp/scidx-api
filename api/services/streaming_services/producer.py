import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
from aiokafka import AIOKafkaProducer
from api.config.kafka_settings import kafka_settings
from .compressor import compress_data
from .stream_processing.kafka_manager import process_kafka_stream
from .stream_processing.url_manager import process_url_stream
from confluent_kafka.admin import AdminClient, KafkaException, KafkaError

KAFKA_SERVER = f"{kafka_settings.kafka_host}:{kafka_settings.kafka_port}"
MAX_STREAMS = kafka_settings.max_streams

logger = logging.getLogger(__name__)

active_producers = []
created_streams = []  # Track active streams by their ID
active_stream_ids = []  # Track stream IDs to ensure sequential assignment

class Producer:
    def __init__(self, filter_semantics, data_streams):
        
        if max_streams_reached():
            raise Exception("Maximum number of streams has been reached. Cannot create more streams.")
        
        self.data_stream_id = get_next_stream_id()
        self.data_streams = data_streams
        self.filter_semantics = filter_semantics
        self.stop_event = asyncio.Event()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.loop = asyncio.get_running_loop()
        self.producer = AIOKafkaProducer(bootstrap_servers=KAFKA_SERVER)
        self.buffer_lock = asyncio.Lock()
        self.tasks = []
        self.retry_limit = 5
        self.retry_attempts = {}

        logger.info(f"Producer initialized with ID: {self.data_stream_id}")
        created_streams.append(self.data_stream_id)

    async def run(self):
        """Start the Kafka producer and begin streaming data from all streams."""
        await self.producer.start()
        logger.info(f"Producer started for data stream ID: {self.data_stream_id}")
        try:
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
                    self.loop,
                    self.stop_event
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
        retries = self.retry_attempts.get(stream, 0)
        if retries < self.retry_limit:
            self.retry_attempts[stream] = retries + 1
            backoff_time = 2 ** retries
            logger.info(f"Retrying stream {resource.format} in {backoff_time} seconds...")
            await asyncio.sleep(backoff_time)
            await self.process_stream(stream)
        else:
            logger.error(f"Retry limit reached for {resource.format}, skipping further retries.")

    async def send_data(self, df, stream, loop):
        """Send data to Kafka in compressed format."""
        data_structure = {"values": {}, "stream_info": stream.extras}
        for col in df.columns:
            data_structure["values"][col] = df[col].tolist()

        compressed_data = compress_data(data_structure)
        await self.producer.send_and_wait(f"{kafka_settings.kafka_prefix}_{self.data_stream_id}", compressed_data)

    async def stop(self):
        """Stop the producer and cancel all ongoing tasks."""
        logger.info("Stopping all producer tasks...")
        self.stop_event.set()
        
        for task in self.tasks:
            task.cancel()

        await asyncio.gather(*self.tasks, return_exceptions=True)
        await self.shutdown_producer()
        
    async def shutdown_producer(self):
        """Shutdown Kafka producer and thread pool."""
        await self.producer.stop()
        self.executor.shutdown(wait=False)
        logger.info(f"Producer stopped for data stream ID: {self.data_stream_id}")


async def delete_all_created_streams():
    """Delete all created Kafka topics based on the created_streams list."""
    logger.info("Deleting all created Kafka topics...")
    
    if not created_streams:
        logger.info("No streams to delete.")
        return

    # Use a set to ensure there are no duplicate topics
    unique_topics_to_delete = {f"{kafka_settings.kafka_prefix}_{stream_id}" for stream_id in created_streams}

    try:
        admin_client = AdminClient({'bootstrap.servers': KAFKA_SERVER})
        topics_to_delete_list = list(unique_topics_to_delete)

        logging.info(f"Found the following unique topics to delete: {topics_to_delete_list}")

        fs = admin_client.delete_topics(topics_to_delete_list, operation_timeout=30)

        for topic, f in fs.items():
            try:
                f.result()  # This may raise an exception, even if the topic was deleted
                logging.info(f"Deleted Kafka topic {topic}")
            except KafkaException as ke:
                pass
            except Exception as e:
                logger.error(f"Failed to delete topic {topic} due to an unexpected error: {e}")
        
        # Clear the created_streams list after successful deletion
        created_streams.clear()

    except KafkaException as e:
        logger.error(f"Kafka error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

        
        
def get_next_stream_id():
    """
    Get the next available stream ID in sequence.
    """
    # Find the first available ID in the sequence starting from 1
    for stream_id in range(1, MAX_STREAMS + 1):
        topic_name = f"{kafka_settings.kafka_prefix}_{stream_id}"
        if stream_id not in active_stream_ids and topic_name not in created_streams:
            active_stream_ids.append(stream_id)  # Reserve this ID
            created_streams.append(topic_name)  # Track the creation
            return stream_id
    
    raise Exception("No available stream IDs. Maximum number of streams reached.")


def max_streams_reached():
    """
    Check if the maximum number of streams has been reached.
    """
    return len(active_stream_ids) >= MAX_STREAMS

def release_stream_id(stream_id):
    """
    Release a stream ID when the stream is stopped or deleted.
    """
    if stream_id in active_stream_ids:
        active_stream_ids.remove(stream_id)
        logger.info(f"Stream ID {stream_id} has been released.")


async def delete_specific_stream(stream_id_or_name: str):
    """
    Delete a specific Kafka topic by its stream ID or full topic name.
    If the input is an integer (e.g., '1'), it assumes the topic name follows
    the 'data_stream_{stream_id}' format. If it's a string, it will delete the topic with that exact name.
    """
    # Determine if the input is a number (stream ID) or full topic name
    if stream_id_or_name.isdigit():
        stream_id = int(stream_id_or_name)
        topic = f"{kafka_settings.kafka_prefix}_{stream_id}"
    else:
        topic = stream_id_or_name

    try:
        # Check if the stream ID exists in the active_stream_ids
        if stream_id_or_name.isdigit() and stream_id in active_stream_ids:
            logger.info(f"Releasing stream ID: {stream_id}")
            release_stream_id(stream_id)  # Release the stream ID upon deletion
        
        # Delete the topic from Kafka
        admin_client = AdminClient({'bootstrap.servers': KAFKA_SERVER})
        logger.info(f"Deleting Kafka topic: {topic}")
        fs = admin_client.delete_topics([topic], operation_timeout=30)

        for t, f in fs.items():
            try:
                f.result()  # The result itself is None if successful
                logger.info(f"Deleted Kafka topic {topic}")
            except Exception as e:
                logger.error(f"Failed to delete topic {topic}: {e}")
                raise Exception(f"Failed to delete Kafka topic '{topic}': {e}")
        
        # Ensure the topic is removed from both created_streams and active_stream_ids
        if stream_id_or_name.isdigit():
            if stream_id in active_stream_ids:
                active_stream_ids.remove(stream_id)
                logger.info(f"Stream ID {stream_id} removed from active_stream_ids.")

        # Remove the full topic name from created_streams (whether name or ID)
        if topic in created_streams:
            created_streams.remove(topic)
            logger.info(f"Removed topic {topic} from created_streams")

    except KafkaException as e:
        logger.error(f"Kafka error: {e}")
        raise Exception(f"Kafka error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise Exception(f"Unexpected error: {e}")
