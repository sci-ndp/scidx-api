from ckanapi import NotFound
from api.config.ckan_settings import ckan_settings

def delete_dataset(dataset_name: str = None, resource_id: str = None):
    """
    Delete a dataset from CKAN by its name.

    Parameters
    ----------
    dataset_name : str
        The name of the dataset to be deleted.
    resource_id : str
        The id of the dataset to be deleted.

    Raises
    ------
    Exception
        If there is an error deleting the dataset.
    """
    ckan = ckan_settings.ckan
    if not (dataset_name or resource_id):
        raise ValueError("must dataset_name and dataset_id cannot both be None.")

    try:
        # Retrieve the dataset to ensure it exists
        if dataset_name:
            dataset = ckan.action.package_show(id=dataset_name)
            if resource_id and resource_id != dataset['id']:
                raise ValueError(f"provided resource_id {resource_id} but {dataset_name} matches id {dataset['id']}.")
            resource_id = dataset['id']
        print(f"Dataset '{dataset_name}' found with ID: {resource_id}")

        # Attempt to delete the dataset using its ID
        ckan.action.dataset_purge(id=resource_id)
        print(f"Dataset '{dataset_name}' successfully deleted.")
    except NotFound:
        raise Exception(f"Dataset '{dataset_name}' not found.")
    except Exception as e:
        raise Exception(f"Error deleting dataset '{dataset_name}': {str(e)}")
