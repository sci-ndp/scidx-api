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
def update_url(dataset_id, resource_name=None, resource_title=None, owner_org=None, resource_url=None, notes=None, extras=None):
    """
    Update a URL dataset and its associated metadata.

    Parameters
    ----------
    dataset_id : str
        The ID of the dataset to be updated.
    resource_name : Optional[str]
        The name of the resource.
    resource_title : Optional[str]
        The title of the resource.
    owner_org : Optional[str]
        The ID of the organization to which the resource belongs.
    resource_url : Optional[str]
        The URL of the resource.
    notes : Optional[str]
        Additional notes about the resource.
    extras : Optional[dict]
        Additional metadata to be added to the resource as extras.

    Returns
    -------
    str
        The ID of the updated resource if successful.

    Raises
    ------
    ValueError
        If any input parameter is invalid.
    KeyError
        If any reserved key is found in the extras.
    Exception
        If there is an error updating the resource, an exception is raised with a detailed message.
    """

    if extras and RESERVED_KEYS.intersection(extras):
        raise KeyError(f"Extras contain reserved keys: {RESERVED_KEYS.intersection(extras)}")

    ckan = ckan_settings.ckan

    try:
        # Get the existing dataset
        dataset = ckan.action.package_show(id=dataset_id)

        # Update the dataset fields if provided
        if resource_name:
            dataset['name'] = resource_name
        if resource_title:
            dataset['title'] = resource_title
        if owner_org:
            dataset['owner_org'] = owner_org
        if notes:
            dataset['notes'] = notes
        if extras:
            existing_extras = {extra['key']: extra['value'] for extra in dataset.get('extras', [])}
            existing_extras.update(extras)
            dataset['extras'] = [{'key': k, 'value': v} for k, v in existing_extras.items()]

        # Update the dataset in CKAN
        updated_dataset = ckan.action.package_update(**dataset)

        # Update the resource if URL is provided
        if resource_url:
            resource = next((res for res in updated_dataset['resources'] if res['format'] == 'url'), None)
            if resource:
                resource['url'] = resource_url
                resource['description'] = f"Resource pointing to {resource_url}"
                ckan.action.resource_update(**resource)

        return updated_dataset['id']

    except Exception as e:
        raise Exception(f"Error updating URL resource: {str(e)}")
