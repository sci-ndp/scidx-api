from typing import List
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from api.config.ckan_settings import ckan_settings
from api.services.default_services import log_retry_attempt

@retry(
    wait=wait_exponential(multiplier=1, max=2),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(Exception),
    after=log_retry_attempt
)
def list_organization() -> List[str]:
    """
    Retrieve a list of all organizations.

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
        organizations = ckan.action.organization_list()
        return organizations

    except Exception as e:
        raise Exception(f"Error retrieving list of organizations: {str(e)}")
