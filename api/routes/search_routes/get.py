from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from api.services import datasource_services
from api.models import DataSourceResponse

router = APIRouter()

@router.get(
    "/",
    response_model=List[DataSourceResponse],
    summary="Search data sources",
    description="Search datasets by various parameters including dataset name, title, organization ID, organization name, resource URL, resource name, dataset description, resource description, resource format, and a general search term."
)
async def search_datasource(
    dataset_name: Optional[str] = Query(None, description="The name of the dataset."),
    dataset_title: Optional[str] = Query(None, description="The title of the dataset."),
    organization_id: Optional[str] = Query(None, description="The ID of the organization that owns the dataset."),
    owner_org: Optional[str] = Query(None, description="The name of the organization that owns the dataset."),
    resource_url: Optional[str] = Query(None, description="The URL of the dataset resource."),
    resource_name: Optional[str] = Query(None, description="The name of the dataset resource."),
    dataset_description: Optional[str] = Query(None, description="The description of the dataset."),
    resource_description: Optional[str] = Query(None, description="The description of the dataset resource."),
    resource_format: Optional[str] = Query(None, description="The format of the dataset resource."),
    search_term: Optional[str] = Query(None, description="A word or fragment of a word to search in any field of the dataset.")  # New parameter
):
    """
    Endpoint to search for datasets based on various parameters.

    Parameters
    ----------
    dataset_name : Optional[str]
        The name of the dataset.
    dataset_title : Optional[str]
        The title of the dataset.
    organization_id : Optional[str]
        The ID of the organization that owns the dataset.
    owner_org : Optional[str]
        The name of the organization that owns the dataset.
    resource_url : Optional[str]
        The URL of the dataset resource.
    resource_name : Optional[str]
        The name of the dataset resource.
    dataset_description : Optional[str]
        The description of the dataset.
    resource_description : Optional[str]
        The description of the dataset resource.
    resource_format : Optional[str]
        The format of the dataset resource.
    search_term : Optional[str]
        A word or fragment of a word to search in any field of the dataset.

    Returns
    -------
    List[DataSourceResponse]
        A list of datasets that match the search criteria.

    Raises
    ------
    HTTPException
        If there is an error during the search, an HTTPException is raised with a detailed message.
    """
    try:
        results = datasource_services.search_datasource(
            dataset_name=dataset_name,
            dataset_title=dataset_title,
            organization_id=organization_id,
            owner_org=owner_org,
            resource_url=resource_url,
            resource_name=resource_name,
            dataset_description=dataset_description,
            resource_description=resource_description,
            resource_format=resource_format,
            search_term=search_term  # Added search_term parameter to the search service
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
