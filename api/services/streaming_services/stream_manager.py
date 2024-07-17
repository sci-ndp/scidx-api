from api.models.request_stream_model import ProducerPayload
from .consumer import consume_kafka_data
from .producer import Producer
from api.services.datasource_services import search_datasource

async def create_stream(payload: ProducerPayload):
    filtered_streams = await search_datasource(search_term=payload.keywords)

    # Ensure only entries with mapping and processing info are included
    filtered_streams = [stream for stream in filtered_streams if stream.extras.get('mapping') and stream.extras.get('processing')]
    
    if not filtered_streams:
        raise ValueError("No data streams found matching the criteria.")

    producer = Producer(payload.filter_semantics, filtered_streams)
    await producer.run()
    return producer.data_stream_id


async def get_stream_data(topic: str):
    async for data in consume_kafka_data(topic):
        yield data
