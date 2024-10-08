import logging
import requests
import asyncio
import pandas as pd
from io import StringIO
import csv
import time
from api.services.streaming_services.data_cleaning import process_and_send_data
import json
import re
from io import StringIO, BytesIO
import xarray as xr
import sseclient  
import aiohttp

logger = logging.getLogger(__name__)

CHUNK_SIZE = 10000
TIME_WINDOW = 10  # seconds
RETRY_LIMIT = 10
BACKOFF_TIME = 5  # Backoff time between retries (in seconds)


async def process_url_stream(stream, filter_semantics, buffer_lock, send_data, loop, stop_event):
    resource_url = stream.resources[0].url
    file_type = stream.extras.get('file_type', None)
    mapping = stream.extras.get('mapping', None)
    processing = stream.extras.get('processing', {})
    logger.info(f"Processing URL stream: {resource_url}, File Type: {file_type}, with mapping {mapping}")

    retries = 0
    timeout_counter = 0

    while retries < RETRY_LIMIT:
        try:
            if file_type in ['CSV', 'TXT', 'NetCDF']:
                # For file-based content: process and stop after completion
                logger.info(f"Fetching data for file-based type ({file_type})...")
                response = requests.get(resource_url)
                response.raise_for_status()  # Raise an exception for bad status codes

                logger.info(f"Successfully fetched data for {file_type}")

                if file_type in ['CSV', 'TXT']:
                    await process_csv_txt_stream(response, processing, mapping, stream, send_data, buffer_lock, loop, filter_semantics)
                elif file_type == 'NetCDF':
                    await process_netcdf_stream(response, processing, mapping, stream, send_data, buffer_lock, loop, filter_semantics)

                logger.info(f"Finished processing {file_type} file, no need to retry.")
                return  # Exit once the file has been processed successfully

            elif file_type == 'json':
                # Process JSON file stream
                response = requests.get(resource_url)
                response.raise_for_status()
                await process_json_stream(response, processing, mapping, stream, send_data, buffer_lock, loop, filter_semantics)

                logger.info(f"Finished processing JSON file stream.")
                return

            elif file_type == 'stream':
                # For stream-based content: retry indefinitely
                while not stop_event.is_set():
                    logger.info(f"Fetching streaming data from {resource_url}...")
                    async with aiohttp.ClientSession() as session:
                        async with session.get(resource_url) as response:
                            response.raise_for_status()  # Raise exception for non-2xx responses
                            logger.info(f"Successfully connected to stream: {resource_url}")
                            await process_streaming_data(response, processing, mapping, stream, send_data, buffer_lock, loop, filter_semantics, stop_event)

                            # If no data received after TIME_WINDOW * 6, stop the stream
                            if timeout_counter >= 6:
                                logger.info(f"No new data received for {6 * TIME_WINDOW} seconds. Stopping the stream.")
                                stop_event.set()

        except requests.RequestException as e:
            logger.error(f"Error fetching data from {resource_url}: {e}. Retrying in {BACKOFF_TIME} seconds...")
            retries += 1
            await asyncio.sleep(BACKOFF_TIME)
        except Exception as e:
            logger.error(f"Unhandled error in URL stream processing: {e}")
            retries += 1
            await asyncio.sleep(BACKOFF_TIME)

    logger.error(f"Retry limit reached ({RETRY_LIMIT}), giving up on {resource_url}")

async def process_csv_txt_stream(response, processing, mapping, stream, send_data, buffer_lock, loop, filter_semantics):
    delimiter = processing.get('delimiter')
    header_line = processing.get('header_line')
    start_line = processing.get('start_line')

    # If any processing info is missing, attempt automatic detection
    if delimiter is None or header_line is None or start_line is None:
        
        sample_data = response.text[:4096]  # Sample the first 4KB of data
        detected_delimiter, detected_header_line, detected_start_line = detect_csv_parameters(sample_data)
        delimiter = delimiter or detected_delimiter
        header_line = header_line if header_line is not None else detected_header_line
        start_line = start_line if start_line is not None else detected_start_line

    # Set defaults if still None
    if delimiter is None:
        delimiter = ',' if stream.extras.get('file_type') == 'CSV' else '\t'
    if header_line is None:
        header_line = 0
    if start_line is None:
        start_line = header_line + 1

    csv_data = StringIO(response.text)

    # Read the first chunk to capture column headers
    first_chunk = pd.read_csv(
        csv_data,
        delimiter=delimiter,
        header=header_line,
        nrows=CHUNK_SIZE,
        skiprows=range(1, start_line) if start_line > 1 else None
    )
    if first_chunk.empty:
        logger.error("No data found in the CSV/TXT stream.")
        return

    # Extract column names from the first chunk
    column_names = first_chunk.columns.tolist()

    start_time = loop.time()
    last_send_time = time.time()

    while True:
        # Read the next chunk and use the same column names
        chunk = pd.read_csv(
            csv_data,
            delimiter=delimiter,
            header=None,  # No header for subsequent chunks
            nrows=CHUNK_SIZE,
            names=column_names,  # Reapply column names
            skiprows=range(1, start_line) if start_line > 1 else None
        )

        if chunk.empty:
            break  # No more data to process

        await process_and_send_data(
            chunk.to_dict(orient='records'),
            mapping,
            stream,
            send_data,
            buffer_lock,
            loop,
            filter_semantics
        )

        elapsed_time = loop.time() - start_time
        time_since_last_send = time.time() - last_send_time

        if time_since_last_send >= TIME_WINDOW or elapsed_time >= TIME_WINDOW:
            break

        last_send_time = time.time()

async def process_json_stream(response, processing, mapping, stream, send_data, buffer_lock, loop, filter_semantics):
    try:
        json_data = response.json()

        # Extract processing keys
        data_key = processing.get('data_key', None)
        info_key = processing.get('info_key', None)
        additional_key = processing.get('additional_key', None)

        # If data_key is not provided, attempt to detect it
        if data_key is None:
            data_key = detect_json_data_key(json_data)
            logger.info(f"Auto-detected data_key: {data_key}")

        # Extract data using the data_key (handle nested keys)
        data = get_nested_json_value(json_data, data_key.split('.')) if data_key else json_data

        # Handle additional info and context keys if they exist
        additional_info = get_nested_json_value(json_data, additional_key.split('.')) if additional_key else None
        info = get_nested_json_value(json_data, info_key.split('.')) if info_key else None

        # Send data in chunks
        start_time = loop.time()
        last_send_time = time.time()

        data_df = pd.DataFrame(data)

        while not data_df.empty:
            chunk = data_df.iloc[:CHUNK_SIZE]
            data_df = data_df.iloc[CHUNK_SIZE:]

            await process_and_send_data(
                chunk.to_dict(orient='records'),
                mapping,
                stream,
                send_data,
                buffer_lock,
                loop,
                filter_semantics
            )

            elapsed_time = loop.time() - start_time
            time_since_last_send = time.time() - last_send_time

            # Break the loop if time window is exceeded
            if time_since_last_send >= TIME_WINDOW or elapsed_time >= TIME_WINDOW:
                break

            last_send_time = time.time()  # Reset the last send time

    except Exception as e:
        logger.error(f"Error processing JSON stream: {e}")

async def process_netcdf_stream(response, processing, mapping, stream, send_data, buffer_lock, loop, filter_semantics):
    try:
        content = response.content  # Get byte content directly
        file_object = BytesIO(content)  # Wrap it into a BytesIO object

        group = processing.get('group', None)

        # Load NetCDF dataset, with or without group
        if group:
            logger.info(f"Loading NetCDF dataset with group '{group}'...")
            ds = xr.open_dataset(file_object, engine='h5netcdf', group=group)
        else:
            logger.info(f"Loading NetCDF dataset (no group specified). Processing entire dataset.")
            ds = xr.open_dataset(file_object, engine='h5netcdf')

        # Ensure mapping is present or fallback to default behavior
        if not mapping:
            logger.info("No mapping provided. Attempting to use all variables from the dataset.")
            mapping = {var: var for var in ds.variables}

        # Verify the variables in mapping exist in the dataset
        missing_vars = [var for var in mapping.values() if var not in ds.variables]
        if missing_vars:
            raise ValueError(f"Missing variables in dataset: {missing_vars}")

        # Extract the selected data from the dataset
        selected_data = ds[list(mapping.values())]
        full_df = selected_data.to_dataframe().reset_index()

        # Drop rows with missing data (optional, based on your needs)
        full_df = full_df.dropna(subset=list(mapping.values()))

        # Process the data in chunks
        start_time = loop.time()
        last_send_time = time.time()

        while not full_df.empty:
            chunk = full_df.iloc[:CHUNK_SIZE]
            full_df = full_df.iloc[CHUNK_SIZE:]

            await process_and_send_data(
                chunk.to_dict(orient='records'),
                mapping,
                stream,
                send_data,
                buffer_lock,
                loop,
                filter_semantics
            )

            elapsed_time = loop.time() - start_time
            time_since_last_send = time.time() - last_send_time

            # Break if time window is exceeded
            if time_since_last_send >= TIME_WINDOW or elapsed_time >= TIME_WINDOW:
                break

            last_send_time = time.time()  # Reset the last send time

        ds.close()

    except Exception as e:
        logger.error(f"Error processing NetCDF stream: {e}")

async def process_streaming_data(response, processing, mapping, stream, send_data, buffer_lock, loop, filter_semantics, stop_event):
    logger.info("Starting dynamic stream processing...")
    retries = 0  # Track the number of retries

    try:
        buffer = ""
        data_key = processing.get('data_key', None)
        stream_type = detect_stream_format(response.headers)
        accumulated_data = []
        last_send_time = time.time()  # Track the last time data was sent
        logger.info(f"Detected stream type: {stream_type}")

        async for line in response.content:
            if stop_event.is_set():
                logger.info("Stop event set. Exiting streaming loop.")
                break  # Stop processing if stop event is set

            try:
                line_str = line.decode('utf-8').strip()

                if not line_str:
                    continue

                if stream_type == "sse":
                    if line_str.startswith("data: "):
                        json_data_str = line_str[6:].strip()
                        buffer += json_data_str

                        try:
                            json_data = json.loads(buffer)
                            buffer = ""

                            if data_key:
                                data = get_nested_json_value(json_data, data_key.split('.'))
                            else:
                                data = flatten_json(json_data)  # Flatten the entire JSON object

                            accumulated_data.append(data)

                            if time.time() - last_send_time >= TIME_WINDOW:
                                await process_and_send_data(
                                    accumulated_data,
                                    mapping,
                                    stream,
                                    send_data,
                                    buffer_lock,
                                    loop,
                                    filter_semantics
                                )
                                logger.info(f"Batch of {len(accumulated_data)} messages sent.")
                                accumulated_data = []
                                last_send_time = time.time()

                        except json.JSONDecodeError:
                            logger.warning("Incomplete JSON detected, continue buffering more data.")
                            continue

                elif stream_type in ["json", "generic"]:
                    buffer += line_str
                    try:
                        json_data = json.loads(buffer)
                        buffer = ""

                        if data_key:
                            data = get_nested_json_value(json_data, data_key.split('.'))
                        else:
                            data = flatten_json(json_data)

                        accumulated_data.append(data)

                        if time.time() - last_send_time >= TIME_WINDOW:
                            await process_and_send_data(
                                accumulated_data,
                                mapping,
                                stream,
                                send_data,
                                buffer_lock,
                                loop,
                                filter_semantics
                            )
                            logger.info(f"Batch of {len(accumulated_data)} messages sent.")
                            accumulated_data = []
                            last_send_time = time.time()

                    except json.JSONDecodeError:
                        logger.warning("Incomplete JSON detected, continue buffering more data.")
                        continue

            except Exception as e:
                logger.error(f"Error during streaming data processing: {e}")
                retries += 1
                if retries >= RETRY_LIMIT:
                    logger.error(f"Maximum retry limit reached ({RETRY_LIMIT}), stopping retry attempts.")
                    break
                logger.info(f"Retrying after error... attempt {retries}/{RETRY_LIMIT}")
                await asyncio.sleep(BACKOFF_TIME * retries)
                continue  # Continue processing on error

        # After the stream ends, send any remaining accumulated data
        if accumulated_data:
            await process_and_send_data(
                accumulated_data,
                mapping,
                stream,
                send_data,
                buffer_lock,
                loop,
                filter_semantics
            )
            logger.info(f"Final batch of {len(accumulated_data)} messages sent.")

    except Exception as e:
        logger.error(f"Unhandled exception during stream processing: {e}")
        await asyncio.sleep(BACKOFF_TIME)

def flatten_json(nested_json, parent_key='', sep='.'):
    """
    Flatten a nested JSON object, creating keys for nested values by joining 
    parent and child keys with the provided separator.
    """
    flat_dict = {}
    for k, v in nested_json.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            flat_dict.update(flatten_json(v, new_key, sep=sep))
        else:
            flat_dict[new_key] = v
    return flat_dict


def get_nested_json_value(data, keys):
    """
    Recursively get nested value from JSON using a list of keys.
    """
    if isinstance(data, list):
        return data  # If it's a list, return the list itself as the main data
    for key in keys:
        data = data.get(key, {})
        if not isinstance(data, dict):
            return data
    return data


def detect_json_data_key (json_data):
    """
    Attempt to detect the key in JSON where the main data resides.
    We'll assume the largest list or dict is the main data.
    If the root JSON is a list, return the list itself.
    """
    if isinstance(json_data, list):
        logger.info("Detected that the root JSON is a list. Returning the list as the data.")
        return None  # No need for a data key; the list is the data

    # Find all potential keys with list or dict as values
    potential_keys = [(key, value) for key, value in json_data.items() if isinstance(value, (list, dict))]

    # Sort potential keys by size (length of list or dict)
    potential_keys.sort(key=lambda item: len(item[1]) if isinstance(item[1], (list, dict)) else 0, reverse=True)

    if potential_keys:
        selected_key = potential_keys[0][0]  # Choose the largest structure by default
        logger.info(f"Auto-detected data key: {selected_key}")
        return selected_key
    
    logger.warning("No suitable data key found. Returning None.")
    return None


def detect_csv_parameters(sample_data):
    """
    Attempts to detect the delimiter, header line, and start line of a CSV/TXT file
    using both sniffer and fallback frequency-based delimiter detection.
    """
    sniffer = csv.Sniffer()
    delimiter = ','
    
    # Try to use csv.Sniffer first
    try:
        dialect = sniffer.sniff(sample_data)
        delimiter = dialect.delimiter
        logger.info(f"Sniffer detected delimiter: {delimiter}")
    except csv.Error:
        # If Sniffer fails, fallback to most frequent non-alphabetic character detection
        logger.info("Sniffer failed, trying to detect delimiter based on frequency.")
        delimiter = detect_frequent_delimiter(sample_data)

    try:
        has_header = sniffer.has_header(sample_data)
        logger.info(f"Sniffer detected header: {has_header}")
    except csv.Error:
        has_header = True  # Default to assuming the file has a header
        logger.info("Sniffer failed to detect header. Assuming header exists.")

    # Set header and start line defaults
    if has_header:
        header_line = 0
        start_line = 1
    else:
        header_line = None
        start_line = 0

    return delimiter, header_line, start_line


def detect_frequent_delimiter(sample_data):
    """
    Detect the most frequent non-alphabetic character in the sample to determine the delimiter.
    """
    # Extract potential delimiters (non-alphabetic, non-numeric, non-space characters)
    potential_delimiters = re.findall(r'[^\w\s]', sample_data)

    if not potential_delimiters:
        logger.warning("No potential delimiters found. Falling back to default comma.")
        return ','  # Fallback to comma

    # Count frequency of each potential delimiter and return the most common
    delimiter_counts = {char: potential_delimiters.count(char) for char in set(potential_delimiters)}
    most_frequent_delimiter = max(delimiter_counts, key=delimiter_counts.get)
    
    logger.info(f"Detected most frequent delimiter: {most_frequent_delimiter}")
    return most_frequent_delimiter


def detect_stream_format(headers):
    """
    Function to detect the type of streaming data based on headers.
    For example, SSE may have headers like `Content-Type: text/event-stream`.
    """
    content_type = headers.get('Content-Type', '').lower()
    
    if "event-stream" in content_type:
        return "sse"
    elif "application/json" in content_type:
        return "json"
    else:
        return "generic"  # Fall back to a generic stream format