import logging
import requests
import asyncio
import pandas as pd
from io import StringIO
import csv
import time
from api.services.streaming_services.data_cleaning import process_and_send_data

logger = logging.getLogger(__name__)

CHUNK_SIZE = 10000
TIME_WINDOW = 10  # seconds

async def process_url_stream(stream, filter_semantics, buffer_lock, send_data, loop):
    resource_url = stream.resources[0].url
    file_type = stream.extras.get('file_type', None)
    mapping = stream.extras.get('mapping', None)
    processing = stream.extras.get('processing', {})

    logger.info(f"Processing URL stream: {resource_url}, File Type: {file_type}, with mapping {mapping}")

    try:
        # Fetch data from the URL
        response = requests.get(resource_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data from {resource_url}")

        # Read the response content based on file type
        if file_type == 'CSV' or file_type == 'TXT':
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
                delimiter = ',' if file_type == 'CSV' else '\t'
            if header_line is None:
                header_line = 0
            if start_line is None:
                start_line = header_line + 1

            csv_data = StringIO(response.text)

            # Process the file in chunks
            start_time = loop.time()
            last_send_time = time.time()

            while True:
                chunk = pd.read_csv(
                    csv_data,
                    delimiter=delimiter,
                    header=header_line,
                    nrows=CHUNK_SIZE,
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

                # Break the loop if time window is exceeded
                if time_since_last_send >= TIME_WINDOW or elapsed_time >= TIME_WINDOW:
                    break

                last_send_time = time.time()  # Reset the last send time

        else:
            logger.info(f"Unsupported file type: {file_type}. Skipping stream.")
            return

    except Exception as e:
        logger.error(f"Error processing URL stream: {e}")



def detect_csv_parameters(sample_data):
    """
    Attempts to detect the delimiter, header line, and start line of a CSV/TXT file.
    """
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(sample_data)
        delimiter = dialect.delimiter
        logger.info(f"Detected delimiter: {delimiter}")
    except csv.Error:
        delimiter = ','  # Default to comma for CSV
        logger.info(f"Could not detect delimiter. Using default: {delimiter}")

    try:
        has_header = sniffer.has_header(sample_data)
        logger.info(f"Detected header: {has_header}")
    except csv.Error:
        has_header = True  # Default to True
        logger.info("Could not detect header. Assuming header exists.")

    if has_header:
        header_line = 0
        start_line = 1
    else:
        header_line = None
        start_line = 0

    return delimiter, header_line, start_line
