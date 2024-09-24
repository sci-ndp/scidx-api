from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Literal
from api.services import datasource_services
from api.models import DataSourceResponse, SearchRequest
from tenacity import RetryError

router = APIRouter()

@router.post(
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
    data: SearchRequest,
):
    """
    Search by various parameters.

    Parameters
    ----------
    data : SearchRequest
        An object containing the parameters of the search

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
        if 'resource_format' in data:
            data['resource_format'] = data['resource_format'].lower()
        results = await datasource_services.search_datasource(**data.dict())
        return results
    except RetryError as e:
        final_exception = e.last_attempt.exception()
        raise HTTPException(status_code=400, detail=str(final_exception))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
