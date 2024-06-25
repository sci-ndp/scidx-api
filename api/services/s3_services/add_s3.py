from api.config.ckan_settings import ckan_settings

def add_s3(
    resource_name, resource_title, owner_org,
    resource_s3, notes=""):
    """
    Add a S3 resource to CKAN.

    Parameters
    ----------
    resource_name : str
        The name of the resource to be created.
    resource_title : str
        The title of the resource to be created.
    owner_org : str
        The ID of the organization to which the resource belongs.
    resource_s3 : str
        The S3 of the resource to be added.
    notes : str, optional
        Additional notes about the resource (default is an empty string).

    Returns
    -------
    str
        The ID of the created resource if successful.

    Raises
    ------
    Exception
        If there is an error creating the resource, an exception is raised with a detailed message.

    Examples
    --------
    >>> add_s3_resource("resource_name", "Resource Title", "org_id", "http://example.com/resource")
    '12345678-abcd-efgh-ijkl-1234567890ab'
    """

    ckan = ckan_settings.ckan

    try:
        # Try to create the resource package in CKAN
        resource_package = ckan.action.package_create(
            name=resource_name,
            title=resource_title,
            owner_org=owner_org,
            notes=notes
        )
        # Retrieve the resource package ID
        resource_package_id = resource_package['id']
    except Exception as e:
        # If an error occurs, raise an exception with a detailed error message
        raise Exception(f"Error creating resource package: {str(e)}")
    
    if resource_package_id:
        try:
            # Try to create the resource within the newly created resource package
            ckan.action.resource_create(
                package_id=resource_package_id,
                url=resource_s3,
                name=resource_name,
                description=f"Resource pointing to {resource_s3}",
                format="s3"
            )
        except Exception as e:
            # If an error occurs, raise an exception with a detailed error message
            raise Exception(f"Error creating resource: {str(e)}")
        
        # If everything goes well, return the resource package ID
        return resource_package_id
    else:
        # This shouldn't happen as the resource package creation should either succeed or raise an exception
        raise Exception("Unknown error occurred")
