from api.config.ckan_settings import ckan_settings
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, RetryError
from api.services.default_services import log_retry_attempt

RESERVED_KEYS = {'name', 'title', 'owner_org', 'notes', 'id', 'resources', 'collection'}

@retry(
    wait=wait_exponential(multiplier=1, max=4),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(Exception),
    after=log_retry_attempt
)
def update_kafka(dataset_id, dataset_name=None, dataset_title=None, owner_org=None, kafka_topic=None, kafka_host=None, kafka_port=None, dataset_description=None, extras=None):
    """
    Update a Kafka dataset and its associated metadata.

    Parameters
    ----------
    dataset_id : str
        The ID of the dataset to be updated.
    dataset_name : Optional[str]
        The name of the dataset.
    dataset_title : Optional[str]
        The title of the dataset.
    owner_org : Optional[str]
        The ID of the organization to which the dataset belongs.
    kafka_topic : Optional[str]
        The Kafka topic name.
    kafka_host : Optional[str]
        The Kafka host.
    kafka_port : Optional[str]
        The Kafka port.
    dataset_description : Optional[str]
        A description of the dataset.
    extras : Optional[dict]
        Additional metadata to be added to the dataset as extras.

    Returns
    -------
    str
        The ID of the updated dataset if successful.

    Raises
    ------
    ValueError
        If any input parameter is invalid.
    KeyError
        If any reserved key is found in the extras.
    Exception
        If there is an error updating the dataset, an exception is raised with a detailed message.
    """

    if extras and RESERVED_KEYS.intersection(extras):
        raise KeyError(f"Extras contain reserved keys: {RESERVED_KEYS.intersection(extras)}")

    ckan = ckan_settings.ckan

    try:
        # Get the existing dataset
        dataset = ckan.action.package_show(id=dataset_id)

        # Update the dataset fields if provided
        if dataset_name:
            dataset['name'] = dataset_name
        if dataset_title:
            dataset['title'] = dataset_title
        if owner_org:
            dataset['owner_org'] = owner_org
        if dataset_description:
            dataset['notes'] = dataset_description
        if extras:
            existing_extras = {extra['key']: extra['value'] for extra in dataset.get('extras', [])}
            existing_extras.update(extras)
            dataset['extras'] = [{'key': k, 'value': v} for k, v in existing_extras.items()]

        # Update the dataset in CKAN
        updated_dataset = ckan.action.package_update(**dataset)

        # Update the resource if Kafka fields are provided
        if kafka_topic or kafka_host or kafka_port:
            resource = next((res for res in updated_dataset['resources'] if res['format'] == 'Kafka'), None)
            if resource:
                if kafka_topic:
                    resource['name'] = kafka_topic
                if kafka_host and kafka_port:
                    resource['url'] = f"{kafka_host};{kafka_port};{resource.get('url', '').split(';')[-1]}"
                ckan.action.resource_update(**resource)

        return updated_dataset['id']

    except Exception as e:
        raise Exception(f"Error updating Kafka dataset: {str(e)}")
