import json
from api.config.ckan_settings import ckan_settings
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from api.services.default_services import log_retry_attempt

RESERVED_KEYS = {'name', 'title', 'owner_org', 'notes', 'id', 'resources', 'collection', 'host', 'port', 'topic', 'mapping', 'processing'}

@retry(
    wait=wait_exponential(multiplier=1, max=2),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(Exception),
    after=log_retry_attempt
)
def update_kafka(
    dataset_id: str,
    dataset_name: str = None,
    dataset_title: str = None,
    owner_org: str = None,
    kafka_topic: str = None,
    kafka_host: str = None,
    kafka_port: str = None,
    dataset_description: str = None,
    extras: dict = None,
    mapping: dict = None,
    processing: dict = None
):
    ckan = ckan_settings.ckan

    try:
        # Fetch the existing dataset
        dataset = ckan.action.package_show(id=dataset_id)
    except Exception as e:
        raise Exception(f"Error fetching Kafka dataset: {str(e)}")

    # Update dataset fields if provided
    if dataset_name:
        dataset['name'] = dataset_name
    if dataset_title:
        dataset['title'] = dataset_title
    if owner_org:
        dataset['owner_org'] = owner_org
    if dataset_description:
        dataset['notes'] = dataset_description

    # Handle extras update
    current_extras = {extra['key']: extra['value'] for extra in dataset.get('extras', [])}
    
    if extras:
        if RESERVED_KEYS.intersection(extras):
            raise KeyError(f"Extras contain reserved keys: {RESERVED_KEYS.intersection(extras)}")
        current_extras.update(extras)

    if mapping:
        current_extras['mapping'] = json.dumps(mapping)

    if processing:
        current_extras['processing'] = json.dumps(processing)

    if kafka_host or kafka_port or kafka_topic:
        if kafka_port and isinstance(kafka_port, str) and kafka_port.isdigit():
            kafka_port = int(kafka_port)
        elif kafka_port and not isinstance(kafka_port, int):
            raise ValueError(f"kafka_port must be an integer, got {type(kafka_port)}")
        
        current_extras['host'] = kafka_host if kafka_host else current_extras.get('host')
        current_extras['port'] = kafka_port if kafka_port else current_extras.get('port')
        current_extras['topic'] = kafka_topic if kafka_topic else current_extras.get('topic')

    dataset['extras'] = [{'key': k, 'value': v} for k, v in current_extras.items()]

    try:
        updated_dataset = ckan.action.package_update(**dataset)
    except Exception as e:
        raise Exception(f"Error updating Kafka dataset: {str(e)}")

    return updated_dataset['id']
