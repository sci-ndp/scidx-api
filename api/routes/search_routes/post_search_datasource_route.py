from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional, Literal
from api.services import datasource_services
from api.models import DataSourceResponse
from tenacity import RetryError
from pydantic import BaseModel

router = APIRouter()

class SearchPayload(BaseModel):
    dataset_name: Optional[str] = None
    dataset_title: Optional[str] = None
    owner_org: Optional[str] = None
    resource_url: Optional[str] = None
    resource_name: Optional[str] = None
    dataset_description: Optional[str] = None
    resource_description: Optional[str] = None
    resource_format: Optional[str] = None
    search_term: Optional[str] = None
    server: Optional[Literal['local', 'global']] = 'local'


@router.post(
    "/search",
    response_model=List[DataSourceResponse],
    summary="Search data sources",
    description="Search datasets by various parameters.",
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
    payload: SearchPayload = Body(...)
):
    """
    Endpoint to search by various parameters using a POST request.

    Parameters
    ----------
    payload : SearchPayload
        The search parameters as a JSON object.

    Returns
    -------
    List[DataSourceResponse]
        A list of datasets that match the search criteria.

    Raises
    ------
    HTTPException
        If there is an error searching for the datasets, an HTTPException is raised with a detailed message.
    """
    try:
        results = await datasource_services.search_datasource(
            dataset_name=payload.dataset_name,
            dataset_title=payload.dataset_title,
            owner_org=payload.owner_org,
            resource_url=payload.resource_url,
            resource_name=payload.resource_name,
            dataset_description=payload.dataset_description,
            resource_description=payload.resource_description,
            resource_format=payload.resource_format.lower() if payload.resource_format else None,
            search_term=payload.search_term,
            server=payload.server
        )
        return results
    except RetryError as e:
        final_exception = e.last_attempt.exception()
        raise HTTPException(status_code=400, detail=str(final_exception))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
