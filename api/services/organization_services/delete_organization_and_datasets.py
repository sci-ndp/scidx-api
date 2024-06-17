from ckanapi import NotFound, ValidationError
from api.config.ckan_settings import ckan_settings


def delete_organization_and_datasets(organization_id: str) -> str:
    """
    Delete an organization and all its datasets in CKAN.

    Parameters
    ----------
    organization_id : str
        The ID of the organization to delete.

    Returns
    -------
    str
        A message confirming the deletion of the organization and its datasets.

    Raises
    ------
    Exception
        If there is an error deleting the organization or its datasets.
    """
    ckan = ckan_settings.ckan

    try:
        # Get all datasets for the organization
        datasets = ckan.action.package_search(fq=f'owner_org:{organization_id}', rows=1000)
        
        # Delete all datasets associated with the organization
        for dataset in datasets['results']:
            ckan.action.package_delete(id=dataset['id'])

        # Delete the organization
        ckan.action.organization_delete(id=organization_id)

        return f"Organization {organization_id} and all its datasets have been deleted."

    except ValidationError as e:
        raise Exception(f"Validation error: {e.error_dict}")
    except NotFound:
        raise Exception("CKAN API endpoint not found or organization does not exist")
    except Exception as e:
        raise Exception(f"Error deleting organization and its datasets: {str(e)}")
