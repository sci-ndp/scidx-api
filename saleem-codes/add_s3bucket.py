from api.config.ckan_settings import ckan_settings

def construct_s3_url(bucket_name):
    base_url = "https://{}.s3.amazonaws.com/index.html"
    return base_url.format(bucket_name)

def add_s3bucket(
    bucket_name, bucket_title, owner_org, notes=""):
    """
    Add a pointer to an S3 bucket to CKAN.

    Parameters
    ----------
    bucket_name : str
        The name of the S3 bucket to be pointed to.
    bucket_title : str
        The title of the S3 bucket pointer to be created.
    owner_org : str
        The ID of the organization to which the pointer belongs.
    notes : str, optional
        Additional notes about the pointer (default is an empty string).

    Returns
    -------
    str
        The ID of the created pointer if successful.

    Raises
    ------
    Exception
        If there is an error creating the pointer, an exception is raised with a detailed message.

    Examples
    --------
    >>> add_s3bucket("noaa-goes18", "NOAA GOES-18 Bucket", "org_id")
    '12345678-abcd-efgh-ijkl-1234567890ab'
    """

    ckan = ckan_settings.ckan

    try:
        # Try to create the pointer in CKAN
        pointer = ckan.action.package_create(
            name=bucket_name,
            title=bucket_title,
            owner_org=owner_org,
            notes=notes
        )
        # Retrieve the pointer ID
        pointer_id = pointer['id']
    except Exception as e:
        # If an error occurs, raise an exception with a detailed error message
        raise Exception(f"Error creating pointer: {str(e)}")
    
    if pointer_id:
        try:
            # Construct the resource URL using the S3 bucket name
            resource_url = construct_s3_url(bucket_name)
            
            # Try to create the resource within the newly created pointer
            ckan.action.resource_create(
                package_id=pointer_id,
                url=resource_url,
                name=bucket_name,
                description=f"Pointer to S3 bucket {bucket_name}",
                format="html"
            )
        except Exception as e:
            # If an error occurs, raise an exception with a detailed error message
            raise Exception(f"Error creating resource: {str(e)}")
        
        # If everything goes well, return the pointer ID
        return pointer_id
    else:
        # This shouldn't happen as the pointer creation should either succeed or raise an exception
        raise Exception("Unknown error occurred")
