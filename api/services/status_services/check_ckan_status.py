from ckanapi import NotFound
from api.config.ckan_settings import ckan_settings


def check_ckan_status() -> bool:
    """
    Check if CKAN is active and reachable.

    Returns
    -------
    bool
        True if CKAN is active, False otherwise.

    Raises
    ------
    Exception
        If there is an error connecting to CKAN.
    """
    ckan = ckan_settings.ckan

    try:
        # Make a request to the status endpoint of CKAN
        status = ckan.action.status_show()
        return True if status else False
    except NotFound:
        return False
    except Exception as e:
        raise Exception(f"Error checking CKAN status: {str(e)}")
