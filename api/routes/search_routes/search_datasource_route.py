from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Literal
from api.services import datasource_services
from api.models import DataSourceResponse, SearchRequest
from tenacity import RetryError

router = APIRouter()

@router.get(
    "/search",
    response_model=List[DataSourceResponse],
    summary="Search data sources",
    description=(
        "Search datasets by various parameters."
    ),
    responses={
        200: {
            "description": "Datasets retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "12345678-abcd-efgh-ijkl-1234567890ab",
                            "name": "example_dataset_name",
                            "title": "Example Dataset Title",
                            "owner_org": "example_org_name",
                            "description": "This is an example dataset.",
                            "resources": [
                                {
                                    "id": "abcd1234-efgh5678-ijkl9012-mnop3456",
                                    "url": "http://example.com/resource",
                                    "name": "Example Resource Name",
                                    "description": "This is an example resource.",
                                    "format": "CSV"
                                }
                            ],
                            "extras": {
                                "key1": "value1",
                                "key2": "value2"
                            }
                        }
                    ]
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error message explaining the bad request"
                    }
                }
            }
        }
    }
)
async def search_datasource(
     dataset_name: Optional[str] = Query(None, description="The name of the dataset."),
    dataset_title: Optional[str] = Query(None, description="The title of the dataset."),
    owner_org: Optional[str] = Query(None, description="The name of the organization."),
    resource_url: Optional[str] = Query(None, description="The URL of the dataset resource."),
    resource_name: Optional[str] = Query(None, description="The name of the dataset resource."),
    dataset_description: Optional[str] = Query(None, description="The description of the dataset."),
    resource_description: Optional[str] = Query(None, description="The description of the dataset resource."),
    resource_format: Optional[str] = Query(None, description="The format of the dataset resource."),
    search_term: Optional[str] = Query(None, description="A term to search across all fields."),
    timestamp: Optional[str] = Query(None, description="A time range term to filter results."),
    server: Optional[Literal['local', 'global']] = Query(
        'local', description="Specify the server to search on: 'local' or 'global'."
    )
):
    """
    Endpoint to search by various parameters.

    Parameters
    ----------
    dataset_name : Optional[str]
        The name of the dataset.
    dataset_title : Optional[str]
        The title of the dataset.
    owner_org : Optional[str]
        The name of the organization.
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
        A term to search across all fields. Multiple values can be provided, separated by commas.
    timestamp: Optional[str]
        A time range term to filter results.
    server : Optional[str]
        Specify the server to search on: 'local' or 'global'.

    Returns
    -------
    List[DataSourceResponse]
        A list of datasets that match the search criteria.

    Raises
    ------
    HTTPException
        If there is an error searching for the datasets, an HTTPException is 
        raised with a detailed message.
    """
    try:
        results = await datasource_services.search_datasource(
            dataset_name=dataset_name,
            dataset_title=dataset_title,
            owner_org=owner_org,
            resource_url=resource_url,
            resource_name=resource_name,
            dataset_description=dataset_description,
            resource_description=resource_description,
            resource_format=resource_format.lower() if resource_format else None,
            search_term=search_term,
            timestamp=timestamp,
            server=server
        )
        return results
    except RetryError as e:
        final_exception = e.last_attempt.exception()
        raise HTTPException(status_code=400, detail=str(final_exception))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))