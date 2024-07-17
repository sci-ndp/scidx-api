from ckanapi import NotFound
from api.config.ckan_settings import ckan_settings

def delete_organization(organization_name: str):
    """
    Delete an organization from CKAN by its name.

    Parameters
    ----------
    organization_name : str
        The name of the organization to be deleted.

    Raises
    ------
    Exception
        If there is an error deleting the organization.
    """
    ckan = ckan_settings.ckan

    try:
        # Retrieve the organization to ensure it exists and get its ID
        organization = ckan.action.organization_show(id=organization_name)
        organization_id = organization['id']

        # Delete all datasets associated with the organization
        datasets = ckan.action.package_search(fq=f'owner_org:{organization_id}', rows=1000)
        for dataset in datasets['results']:
            ckan.action.dataset_delete(id=dataset['id'])
            ckan.action.dataset_purge(id=dataset['id'])

        # Delete the organization
        ckan.action.organization_delete(id=organization_id)
        ckan.action.organization_purge(id=organization_id)
    except NotFound:
        raise Exception("Organization not found")
    except Exception as e:
        raise Exception(f"Error deleting organization: {str(e)}")
