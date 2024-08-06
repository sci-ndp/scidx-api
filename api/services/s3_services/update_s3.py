import json
from typing import Dict, Optional
from api.config.ckan_settings import ckan_settings
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from api.services.default_services import log_retry_attempt

RESERVED_KEYS = {'name', 'title', 'owner_org', 'notes', 'id', 'resources', 'collection'}

@retry(
    wait=wait_exponential(multiplier=1, max=2),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(Exception),
    after=log_retry_attempt
)
async def update_s3(
    resource_id: str,
    resource_name: Optional[str] = None,
    resource_title: Optional[str] = None,
    owner_org: Optional[str] = None,
    resource_s3: Optional[str] = None,
    notes: Optional[str] = None,
    extras: Optional[Dict[str, str]] = None
):
    ckan = ckan_settings.ckan

    try:
        # Fetch the existing resource
        resource = ckan.action.package_show(id=resource_id)
    except Exception as e:
        raise Exception(f"Error fetching S3 resource: {str(e)}")

    # Update resource fields if provided
    if resource_name:
        resource['name'] = resource_name
    if resource_title:
        resource['title'] = resource_title
    if owner_org:
        resource['owner_org'] = owner_org
    if notes:
        resource['notes'] = notes

    # Handle extras update
    current_extras = {extra['key']: extra['value'] for extra in resource.get('extras', [])}
    
    if extras:
        if RESERVED_KEYS.intersection(extras):
            raise KeyError(f"Extras contain reserved keys: {RESERVED_KEYS.intersection(extras)}")
        current_extras.update(extras)

    resource['extras'] = [{'key': k, 'value': v} for k, v in current_extras.items()]

    try:
        # Update the resource package in CKAN
        updated_resource = ckan.action.package_update(**resource)

        # If the S3 URL is updated, update the corresponding resource
        if resource_s3:
            for res in resource['resources']:
                if res['format'].lower() == 's3':
                    ckan.action.resource_update(id=res['id'], url=resource_s3, package_id=resource_id)
                    break
    except Exception as e:
        raise Exception(f"Error updating S3 resource: {str(e)}")

    return updated_resource['id']
