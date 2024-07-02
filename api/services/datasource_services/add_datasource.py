from api.config.ckan_settings import ckan_settings

# Define a set of reserved keys that should not be used in the extras
RESERVED_KEYS = {'name', 'title', 'owner_org', 'notes', 'id', 'resources', 'collection'}

def add_datasource(
    dataset_name, dataset_title, owner_org,
    resource_url, resource_name,
    dataset_description="", resource_description="", resource_format=None, extras=None):
    """
    Add a dataset and its associated resource to CKAN.

    Parameters
    ----------
    dataset_name : str
        The name of the dataset to be created.
    dataset_title : str
        The title of the dataset to be created.
    owner_org : str
        The ID of the organization to which the dataset belongs.
    resource_url : str
        The URL of the resource to be associated with the dataset.
    resource_name : str
        The name of the resource to be associated with the dataset.
    dataset_description : str, optional
        A description of the dataset (default is an empty string).
    resource_description : str, optional
        A description of the resource (default is an empty string).
    resource_format : str, optional
        The format of the resource (default is None).
    extras : dict, optional
        Additional metadata to be added to the dataset as extras (default is None).

    Returns
    -------
    str
        The ID of the created dataset if successful.

    Raises
    ------
    ValueError
        If any input parameter is invalid.
    KeyError
        If any reserved key is found in the extras.
    Exception
        If there is an error creating the dataset or adding the resource, an
        exception is raised with a detailed message.
    """
    
    if not isinstance(extras, (dict, type(None))):
        raise ValueError("Extras must be a dictionary or None.")

    if extras and RESERVED_KEYS.intersection(extras):
        raise KeyError(f"Extras contain reserved keys: {RESERVED_KEYS.intersection(extras)}")

    ckan = ckan_settings.ckan

    try:
        # Create the dataset in CKAN with additional extras if provided
        dataset_dict = {
            'name': dataset_name,
            'title': dataset_title,
            'owner_org': owner_org,
            'notes': dataset_description
        }

        if extras:
            dataset_dict['extras'] = [{'key': k, 'value': v} for k, v in extras.items()]

        dataset = ckan.action.package_create(**dataset_dict)

        # Retrieve the dataset ID
        dataset_id = dataset['id']
    except Exception as e:
        # If an error occurs, raise an exception with a detailed error message
        raise Exception(f"Error creating dataset: {str(e)}")
    
    if dataset_id:
        try:
            # Create the resource within the newly created dataset
            ckan.action.resource_create(
                package_id=dataset_id,
                url=resource_url,
                name=resource_name,
                description=resource_description,
                format=resource_format
            )
        except Exception as e:
            # If an error occurs, raise an exception with a detailed error message
            raise Exception(f"Error creating resource: {str(e)}")
        
        # If everything goes well, return the dataset ID
        return dataset_id
    else:
        # This shouldn't happen as the dataset creation should either succeed or raise an exception
        raise Exception("Unknown error occurred")
