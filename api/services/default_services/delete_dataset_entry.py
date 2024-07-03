from api.config.ckan_settings import ckan_settings
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, RetryError
from api.services.default_services import log_retry_attempt

@retry(
    wait=wait_exponential(multiplier=1, max=4),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(Exception),
    after=log_retry_attempt
)
def delete_dataset(dataset_id):
    """
    Delete a dataset by its ID.

    Parameters
    ----------
    dataset_id : str
        The ID of the dataset to be deleted.

    Returns
    -------
    str
        A message indicating the dataset has been deleted.

    Raises
    ------
    Exception
        If there is an error deleting the dataset.
    """
    ckan = ckan_settings.ckan

    try:
        ckan.action.dataset_purge(id=dataset_id)
        return "Dataset deleted successfully"
    except Exception as e:
        raise Exception(f"Error deleting dataset: {str(e)}")
