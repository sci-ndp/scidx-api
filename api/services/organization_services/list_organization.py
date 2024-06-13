from ckanapi import NotFound
from api.config.ckan_settings import ckan_settings
from typing import List


def list_organization() -> List[str]:
    """
    List all organizations in CKAN.

    Returns
    -------
    List[str]
        A list of organization names.

    Raises
    ------
    Exception
        If there is an error retrieving the list of organizations.
    """
    ckan = ckan_settings.ckan

    try:
        # Retrieve the list of organizations
        organizations = ckan.action.organization_list()
        return organizations
    except NotFound:
        raise Exception("CKAN API endpoint not found")
    except Exception as e:
        raise Exception(f"Error retrieving organizations: {str(e)}")
