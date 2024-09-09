import logging
import requests
import asyncio
import pandas as pd
from api.services.streaming_services.data_cleaning import process_and_send_data

logger = logging.getLogger(__name__)

async def process_url_stream(stream, filter_semantics, buffer_lock, send_data, loop):
    resource_url = stream.resources[0].url
    file_type = stream.extras.get('file_type', None)
    
    mapping = stream.extras.get('mapping', None)
    processing = stream.extras.get('processing', {})

    logger.info(f"Processing URL stream: {resource_url},/n {file_type},/n {processing}/n with mapping {mapping}")
    
    

    # try:
    #     # Fetch data from the URL (consider switching to aiohttp for async if needed)
    #     response = requests.get(resource_url)
    #     if response.status_code != 200:
    #         raise Exception(f"Failed to fetch data from {resource_url}")

    #     data = response.json()  # Assuming the response is JSON format
    #     if data_key:
    #         data = data.get(data_key, [])

    #     if not isinstance(data, list):
    #         data = [data]

    #     additional_info = data.get(info_key, {}) if info_key else None
    #     messages = data

    #     await process_and_send_data(messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics, additional_info)

    # except Exception as e:
    #     logger.error(f"Error processing URL stream: {e}")

