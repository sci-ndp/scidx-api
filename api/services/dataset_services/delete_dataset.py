from ckanapi import NotFound
from api.config.ckan_settings import ckan_settings

def delete_dataset(dataset_name: str):
    """
    Delete a dataset from CKAN by its name.

    Parameters
    ----------
    dataset_name : str
        The name of the dataset to be deleted.

    Raises
    ------
    Exception
        If there is an error deleting the dataset.
    """
    ckan = ckan_settings.ckan

    try:
        # Retrieve the dataset to ensure it exists
        dataset = ckan.action.package_show(id=dataset_name)
        dataset_id = dataset['id']
        print(f"Dataset '{dataset_name}' found with ID: {dataset_id}")

        # Attempt to delete the dataset using its ID
        ckan.action.dataset_purge(id=dataset_id)
        print(f"Dataset '{dataset_name}' successfully deleted.")
    except NotFound:
        raise Exception(f"Dataset '{dataset_name}' not found.")
    except Exception as e:
        raise Exception(f"Error deleting dataset '{dataset_name}': {str(e)}")
