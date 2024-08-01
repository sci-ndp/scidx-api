import pandas as pd
import json
from aiokafka import AIOKafkaConsumer
import asyncio
import logging
import time
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

    # logger.info("DataFrame before filtering:\n%s", df.head())  
    
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
    processing = stream.extras.get('processing', {})
    data_key = processing.get('data_key', None)
    info_key = processing.get('info_key', None)
    logger.info(f"Processing Kafka stream: {kafka_topic} from {kafka_host}:{kafka_port} with mapping {mapping}")

    consumer = AIOKafkaConsumer(
        kafka_topic,
        bootstrap_servers=f"{kafka_host}:{kafka_port}",
        auto_offset_reset='earliest',
        group_id=f"group_{kafka_topic}_{int(time.time())}"  # Ensure unique group to avoid offset issues
    )
    await consumer.start()

    try:
        start_time = loop.time()
        last_send_time = time.time()
        messages = []
        additional_info = None

        while True:
            try:
                message = await asyncio.wait_for(consumer.getone(), timeout=TIME_WINDOW)
                data = json.loads(message.value)
                
                if info_key:
                    additional_info = data.get(info_key, {})

                if data_key:
                    data = data.get(data_key, {})
                
                messages.append(data)
            except asyncio.TimeoutError:
                logger.info("No new messages received in TIME_WINDOW")

            elapsed_time = loop.time() - start_time
            time_since_last_send = time.time() - last_send_time

            # Check if it's time to send the accumulated messages
            if len(messages) >= CHUNK_SIZE or time_since_last_send >= TIME_WINDOW or elapsed_time >= TIME_WINDOW:
                await process_and_send_data(messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics, additional_info)
                messages = []  # Clear the messages list after sending
                start_time = loop.time()
                last_send_time = time.time()  # Reset the last send time

            # Break the loop if no more messages are expected
            if not messages and time_since_last_send >= TIME_WINDOW:
                break

        # Process remaining messages if any after the consumer stops
        if messages:
            # logger.info('FINAL SENDING')
            await process_and_send_data(messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics, additional_info)

    except Exception as e:
        logger.error(f"Error in Kafka stream processing: {e}")

    finally:
        # Ensure consumer stops correctly
        if not consumer._closed:
            await consumer.stop()


async def process_and_send_data(messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics, additional_info=None):
    async with buffer_lock:
        df = pd.DataFrame(messages)
        mapped_data = mapped_values_vectorized(mapping, df)
        filtered_data = apply_filters_vectorized(mapped_data, filter_semantics)
        if not filtered_data.empty:
            if additional_info:
                if isinstance(additional_info, dict):
                    stream.extras.update(additional_info)
                elif isinstance(additional_info, str):
                    stream.extras['additional_info'] = additional_info
                else:
                    stream.extras['additional_info'] = str(additional_info)
            # logger.info("Filtered DataFrame:\n%s", filtered_data.head())
            await send_data(filtered_data, stream, loop)
        else:
            pass
            # logger.info("No data after filtering")
