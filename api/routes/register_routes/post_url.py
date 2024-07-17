from fastapi import APIRouter, HTTPException, status, Depends
from api.services.url_services.add_url import add_url
from api.models.urlrequest_model import URLRequest
from tenacity import RetryError
from typing import Dict, Any

from api.services.keycloak_services.get_current_user import get_current_user

router = APIRouter()

@router.post(
    "/url",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new URL resource",
    description="""
Create a new URL resource in CKAN.

### Common Fields for All File Types
- **resource_name**: The unique name of the resource to be created.
- **resource_title**: The title of the resource to be created.
- **owner_org**: The ID of the organization to which the resource belongs.
- **resource_url**: The URL of the resource to be added.
- **file_type**: The type of the file (`stream`, `CSV`, `TXT`, `JSON`, `NetCDF`).
- **notes**: Additional notes about the resource (optional).
- **extras**: Additional metadata to be added to the resource package as extras (optional).
- **mapping**: Mapping information for the dataset (optional).
- **processing**: Processing information for the dataset, which varies based on the `file_type`.

### File Type-Specific Processing Information

1. **Stream**
    ```json
    {
        "refresh_rate": "5 seconds",
        "data_key": "results"
    }
    ```
    - **refresh_rate**: The refresh rate for the data stream.
    - **data_key**: The key for the response data in the JSON file.

2. **CSV**
    ```json
    {
        "delimiter": ",",
        "header_line": 1,
        "start_line": 2,
        "comment_char": "#"
    }
    ```
    - **delimiter**: The delimiter used in the CSV file.
    - **header_line**: The line number of the header in the CSV file.
    - **start_line**: The line number where the data starts in the CSV file.
    - **comment_char**: The character used for comments in the CSV file (optional).

3. **TXT**
    ```json
    {
        "delimiter": "\t",
        "header_line": 1,
        "start_line": 2
    }
    ```
    - **delimiter**: The delimiter used in the TXT file.
    - **header_line**: The line number of the header in the TXT file.
    - **start_line**: The line number where the data starts in the TXT file.

4. **JSON**
    ```json
    {
        "info_key": "count",
        "additional_key": "",
        "data_key": "results"
    }
    ```
    - **info_key**: The key for additional information in the JSON file (optional).
    - **additional_key**: An additional key in the JSON file (optional).
    - **data_key**: The key for the response data in the JSON file.

5. **NetCDF**
    ```json
    {
        "group": "group_name"
    }
    ```
    - **group**: The group within the NetCDF file (optional).
""",
    responses={
        201: {
            "description": "Resource created successfully",
            "content": {
                "application/json": {
                    "example": {"id": "12345678-abcd-efgh-ijkl-1234567890ab"}
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Error creating resource: <error message>"}
                }
            }
        }
    }
)
async def create_url_resource(
    data: URLRequest,
    _: Dict[str, Any] = Depends(get_current_user)):
    """
    Add a URL resource to CKAN.

    Parameters
    ----------
    data : URLRequest
        An object containing all the required parameters for creating a URL resource.

    Returns
    -------
    dict
        A dictionary containing the ID of the created resource if successful.

    Raises
    ------
    HTTPException
        If there is an error creating the resource, an HTTPException is raised with a detailed message.
    """
    try:
        resource_id = add_url(
            resource_name=data.resource_name,
            resource_title=data.resource_title,
            owner_org=data.owner_org,
            resource_url=data.resource_url,
            file_type=data.file_type,
            notes=data.notes,
            extras=data.extras,
            mapping=data.mapping,
            processing=data.processing
        )
        return {"id": resource_id}
    except RetryError as e:
        final_exception = e.last_attempt.exception()
        raise HTTPException(status_code=400, detail=str(final_exception))
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Reserved key error: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
