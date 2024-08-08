import json
from typing import Any, Dict, Optional

from pydantic import ValidationError
from api.config.ckan_settings import ckan_settings
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from api.models.update_url_model import CSVProcessingInfo, JSONProcessingInfo, NetCDFProcessingInfo, StreamProcessingInfo, TXTProcessingInfo
from api.services.default_services import log_retry_attempt
import logging

logger = logging.getLogger(__name__)
# Define a set of reserved keys that should not be used in the extras
RESERVED_KEYS = {'name', 'title', 'owner_org', 'notes', 'id', 'resources', 'collection', 'url', 'mapping', 'processing', 'file_type'}

@retry(
    wait=wait_exponential(multiplier=1, max=2),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(Exception),
    after=log_retry_attempt
)
async def update_url(
    resource_id: str,
    resource_name: Optional[str] = None,
    resource_title: Optional[str] = None,
    owner_org: Optional[str] = None,
    resource_url: Optional[str] = None,
    file_type: Optional[str] = None,
    notes: Optional[str] = None,
    extras: Optional[Dict[str, str]] = None,
    mapping: Optional[Dict[str, str]] = None,
    processing: Optional[Dict[str, Any]] = None,
):
    ckan = ckan_settings.ckan

    # Fetch the existing resource data
    try:
        resource = ckan.action.package_show(id=resource_id)
    except Exception as e:
        raise Exception(f"Error fetching resource with ID {resource_id}: {str(e)}")

    # Extract current file type and processing from the resource
    current_extras = {extra['key']: extra['value'] for extra in resource.get('extras', [])}
    current_file_type = current_extras.get("file_type")
    current_processing = json.loads(current_extras.get("processing", "{}"))

    # Validate the processing information based on whether the file type has changed or not
    if file_type and file_type != current_file_type:
        # If the file type has changed
        if processing is not None:
            # Even if processing is an empty dict, it should be used to update the resource
            processing = validate_manual_processing_info(file_type, processing)
        else:
            processing = validate_manual_processing_info(file_type, current_processing)
    elif processing is not None:
        # If the file type hasn't changed but processing info is provided
        processing = validate_manual_processing_info(current_file_type, processing)

    # Prepare the updated data
    updated_data = {
        'name': resource_name or resource['name'],
        'title': resource_title or resource['title'],
        'owner_org': owner_org or resource['owner_org'],
        'notes': notes or resource['notes'],
        'extras': resource.get('extras', [])
    }

    # Update the extras with new mapping, processing, and file type if provided
    if file_type:
        current_extras['file_type'] = file_type
    if mapping:
        current_extras['mapping'] = json.dumps(mapping)
    if processing is not None:
        # If processing is explicitly provided (even if empty), update it
        current_extras['processing'] = json.dumps(processing)
    if extras:
        if RESERVED_KEYS.intersection(extras):
            raise KeyError(f"Extras contain reserved keys: {RESERVED_KEYS.intersection(extras)}")
        current_extras.update(extras)

    # Convert back to the expected CKAN format
    updated_data['extras'] = [{'key': k, 'value': v} for k, v in current_extras.items()]

    # Perform the update
    try:
        ckan.action.package_update(id=resource_id, **updated_data)

        # Update the resource URL if it has changed
        if resource_url:
            for res in resource['resources']:
                if res['format'].lower() == 'url':
                    ckan.action.resource_update(id=res['id'], url=resource_url, package_id=resource_id)
                    break
    except Exception as e:
        raise Exception(f"Error updating resource with ID {resource_id}: {str(e)}")

    return {"message": "Resource updated successfully"}


def validate_manual_processing_info(file_type: str, processing: dict):
    """
    Manually validate the processing information based on the file type.
    """

    # Define expected fields for each file type
    expected_fields = {
        "stream": {"refresh_rate", "data_key"},
        "CSV": {"delimiter", "header_line", "start_line", "comment_char"},
        "TXT": {"delimiter", "header_line", "start_line"},
        "JSON": {"info_key", "additional_key", "data_key"},
        "NetCDF": {"group"}
    }

    required_fields = {
        "CSV": {"delimiter", "header_line", "start_line"},
        "TXT": {"delimiter", "header_line", "start_line"},
        # No required fields for the other types as they're all optional
    }

    # Get the expected fields for the current file type
    expected = expected_fields.get(file_type)
    required = required_fields.get(file_type, set())

    # Check for unexpected fields in the provided processing info
    unexpected_fields = set(processing.keys()) - expected

    if unexpected_fields:
        raise ValueError(f"Unexpected fields in processing for {file_type}: {unexpected_fields}")

    # Check for missing required fields
    missing_required_fields = required - set(processing.keys())

    if missing_required_fields:
        raise ValueError(f"Missing required fields in processing for {file_type}: {missing_required_fields}")

    # If it passes all checks, return the validated processing info
    return processing


