import json
from api.config import ckan_settings, dxspaces_settings 
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from api.services.default_services import log_retry_attempt
import dxspaces

# Define a set of reserved keys that should not be used in the extras
RESERVED_KEYS = {'name', 'title', 'owner_org', 'notes', 'id', 'resources', 'collection', 'url', 'mapping', 'processing', 'file_type'}

@retry(
    wait=wait_exponential(multiplier=
                          1, max=2),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(Exception),
    after=log_retry_attempt
)
def add_url(
    resource_name, resource_title, owner_org,
    resource_url, file_type="",notes="", extras=None, mapping=None, processing=None):
    """
    Add a URL resource to CKAN.

    Parameters
    ----------
    resource_name : str
        The name of the resource to be created.
    resource_title : str
        The title of the resource to be created.
    owner_org : str
        The ID of the organization to which the resource belongs.
    resource_url : str
        The URL of the resource to be added.
    notes : str, optional
        Additional notes about the resource (default is an empty string).
    extras : dict, optional
        Additional metadata to be added to the resource package as extras (default is None).
    mapping : dict, optional
        Mapping information for the dataset (default is None).
    processing : dict, optional
        Processing information for the dataset based on the file type (default is None).

    Returns
    -------
    str
        The ID of the created resource if successful.

    Raises
    ------
    ValueError
        If any input parameter is invalid.
    KeyError
        If any reserved key is found in the extras.
    Exception
        If there is an error creating the resource, an exception is raised with a detailed message.
    """

    if not isinstance(extras, (dict, type(None))):
        raise ValueError("Extras must be a dictionary or None.")

    if extras and RESERVED_KEYS.intersection(extras):
        raise KeyError(f"Extras contain reserved keys: {RESERVED_KEYS.intersection(extras)}")

    url_extras = {
        "file_type":file_type
    }

    if dxspaces_settings.registration_methods['url']:
        dxspaces = dxspaces_settings.dxspaces
        staging_params = {'url': resource_url}
        staging_handle = dxspaces.Register('url', resource_name, staging_params)
        extras['staging_handle'] = staging_handle.model_dump_json()

    if mapping:
        url_extras['mapping'] = json.dumps(mapping)

    if processing:
        url_extras['processing'] = json.dumps(processing)

    extras_cleaned = extras.copy() if extras else {}
    extras_cleaned.update(url_extras)
    
    ckan = ckan_settings.ckan

    try:
        # Create the resource package in CKAN with additional extras if provided
        resource_package_dict = {
            'name': resource_name,
            'title': resource_title,
            'owner_org': owner_org,
            'notes': notes,
            'extras': [{'key': k, 'value': v} for k, v in extras_cleaned.items()]
        }

        resource_package = ckan.action.package_create(**resource_package_dict)

        # Retrieve the resource package ID
        resource_package_id = resource_package['id']
    except Exception as e:
        # If an error occurs, raise an exception with a detailed error message
        raise Exception(f"Error creating resource package: {str(e)}")
    
    if resource_package_id:
        try:
            # Create the resource within the newly created resource package
            ckan.action.resource_create(
                package_id=resource_package_id,
                url=resource_url,
                name=resource_name,
                description=f"Resource pointing to {resource_url}",
                format="url"
            )
        except Exception as e:
            # If an error occurs, raise an exception with a detailed error message
            raise Exception(f"Error creating resource: {str(e)}")
        
        # If everything goes well, return the resource package ID
        return resource_package_id
    else:
        # This shouldn't happen as the resource package creation should either succeed or raise an exception
        raise Exception("Unknown error occurred")
