import pandas as pd
import json
from aiokafka import AIOKafkaConsumer
import logging

logger = logging.getLogger(__name__)

CHUNK_SIZE = 10000
TIME_WINDOW = 10  # seconds


def mapped_values_vectorized(mapping, df):
    result = pd.DataFrame(index=df.index)
    for key, path in mapping.items():
        if path in df.columns:
            if 'timestamp' in key.lower():
                result[key] = pd.to_datetime(df[path], errors='coerce').dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            else:
                result[key] = df[path]
    return result

def apply_filters_vectorized(df, filter_semantics):
    if not filter_semantics:
        return df

    for filter_condition in filter_semantics:
        try:
            if '>=' in filter_condition:
                field, condition = filter_condition.split('>=', 1)
                field = field.strip()
                condition = float(condition.strip())
                if field in df.columns:
                    df = df[df[field].astype(float) >= condition]
                else:
                    return pd.DataFrame()  # Return empty DataFrame if field is missing
            elif '>' in filter_condition:
                field, condition = filter_condition.split('>', 1)
                field = field.strip()
                condition = float(condition.strip())
                if field in df.columns:
                    df = df[df[field].astype(float) > condition]
                else:
                    return pd.DataFrame()  # Return empty DataFrame if field is missing
            elif '<=' in filter_condition:
                field, condition = filter_condition.split('<=', 1)
                field = field.strip()
                condition = float(condition.strip())
                if field in df.columns:
                    df = df[df[field].astype(float) <= condition]
                else:
                    return pd.DataFrame()  # Return empty DataFrame if field is missing
            elif '<' in filter_condition:
                field, condition = filter_condition.split('<', 1)
                field = field.strip()
                condition = float(condition.strip())
                if field in df.columns:
                    df = df[df[field].astype(float) < condition]
                else:
                    return pd.DataFrame()  # Return empty DataFrame if field is missing
            elif '!=' in filter_condition:
                field, condition = filter_condition.split('!=', 1)
                field = field.strip()
                condition = condition.strip()
                if field in df.columns:
                    try:
                        df = df[df[field].astype(float) != float(condition)]
                    except ValueError:
                        df = df[df[field] != condition]
                else:
                    return pd.DataFrame()  # Return empty DataFrame if field is missing
            elif '=' in filter_condition:
                field, condition = filter_condition.split('=', 1)
                field = field.strip()
                condition = condition.strip()
                if field in df.columns:
                    try:
                        df = df[df[field].astype(float) == float(condition)]
                    except ValueError:
                        df = df[df[field] == condition]
                else:
                    return pd.DataFrame()  # Return empty DataFrame if field is missing
        except Exception as e:
            logger.error(f"Error applying filter '{filter_condition}': {e}")

    return df

async def process_kafka_stream(stream, filter_semantics, buffer_lock, send_data, loop):
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
        start_time = loop.time()
        messages = []

        async for message in consumer:
            data = json.loads(message.value)
            messages.append(data)

            elapsed_time = loop.time() - start_time
            if elapsed_time >= TIME_WINDOW or len(messages) >= CHUNK_SIZE:
                await process_and_send_data(messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics)
                messages = []
                start_time = loop.time()
    finally:
        await consumer.stop()
        logger.info(f"Consumer stopped for Kafka stream: {kafka_topic}")

async def process_and_send_data(messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics):
    async with buffer_lock:
        df = pd.DataFrame(messages)
        mapped_data = mapped_values_vectorized(mapping, df)
        filtered_data = apply_filters_vectorized(mapped_data, filter_semantics)
        if not filtered_data.empty:
            await send_data(filtered_data, stream, loop)
