from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional, Literal
from api.services import datasource_services
from api.models import DataSourceResponse, SearchRequest
from tenacity import RetryError
from pydantic import BaseModel

router = APIRouter()

@router.post(
    "/search",
    response_model=List[DataSourceResponse],
    summary="Search data sources",
    description=("Search datasets by various parameters.\n\n"
        "### Common registration-matching parameters\n"
        "- **dataset_name**: the name of the dataset\n"
        "- **dataset_title**: the title of the dataset\n"
        "- **owner_org**: the name of the organization\n"
        "- **resource_url**: the URL of the dataset resource\n"
        "- **resource_name**: the name of the dataset resource\n"
        "- **dataset_description**: the description of the dataset\n"
        "- **resource_description**: the description of the dataset resource\n"
        "- **resource_format**: the format of the dataset resource\n\n"
        "### User-defined value search parameters\n"
        "- **search_term**: a comma-separated list of terms to search across"
        " all fields\n"
        "- **filter_list**: a list of field filters of the form `key:value`.\n"
        "- **timestamp**: a filter on the `timestamp` field of results."
        " Timestamp can have one of two formats:\n\n"
        "    `[<>]?YYYY(-MM(-DD(THH(:mm(:ss)))))` - the closeset timestamp"
        " value to that which is provided. `>` (**default**) indicates the"
        " closest in the future, while `<` indicates the closest"
        " in the past.\n"
        "    `(YYYY(-MM(-DD(THH(:mm(:ss))))))?/YYYY(-MM(-DD(THH(:mm(:ss)))))` "
        "- filter results to the specified time interval. A missing timestamp"
        " indicates an open interval.\n"
        "### Unused parameters\n"
        "- **server** - one of `local` or `global`"
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

