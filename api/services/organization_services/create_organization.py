from typing import Optional
from ckanapi import NotFound, ValidationError
from api.config.ckan_settings import ckan_settings

def create_organization(name: str, title: str, description: Optional[str] = None) -> str:
    """
    Create a new organization in CKAN.

    Parameters
    ----------
    name : str
        The name of the organization.
    title : str
        The title of the organization.
    description : Optional[str]
        The description of the organization.

    Returns
    -------
    str
        The ID of the created organization.

    Raises
    ------
    Exception
        If there is an error creating the organization.
    """
    ckan = ckan_settings.ckan

    try:
        # Create the organization in CKAN
        organization = ckan.action.organization_create(
            name=name,
            title=title,
            description=description
        )
        # Return the organization ID
        return organization['id']
    except ValidationError as e:
        raise Exception(f"Validation error: {e.error_dict}")
    except NotFound:
        raise Exception("CKAN API endpoint not found")
    except Exception as e:
        if "Group name already exists in database" in str(e):
            raise Exception("Group name already exists in database")
        raise Exception(f"Error creating organization: {str(e)}")
