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
    description=(
        "Create a new URL resource in CKAN.\n\n"
        "### Common Fields for All File Types\n"
        "- **resource_name**: The unique name of the resource to be created.\n"
        "- **resource_title**: The title of the resource to be created.\n"
        "- **owner_org**: The ID of the organization to which the resource "
        "belongs.\n"
        "- **resource_url**: The URL of the resource to be added.\n"
        "- **file_type**: The type of the file (`stream`, `CSV`, `TXT`, "
        "`JSON`, `NetCDF`).\n"
        "- **notes**: Additional notes about the resource (optional).\n"
        "- **extras**: Additional metadata to be added to the resource "
        "package as extras (optional).\n"
        "- **mapping**: Mapping information for the dataset (optional).\n"
        "- **processing**: Processing information for the dataset is optional "
        "and varies based on the `file_type`. If provided, it must match the "
        "fields required for the specific file type.\n\n"
        "### File Type-Specific Processing Information (Optional)\n"
        "If you provide processing information, ensure it follows the expected "
        "structure for the selected `file_type`. Here are the details for each "
        "type:\n\n"
        "1. **Stream**\n"
        "    ```json\n"
        '    "processing": {\n'
        '        "refresh_rate": "5 seconds",\n'
        '        "data_key": "results"\n'
        "    }\n"
        "    ```\n"
        "    - **refresh_rate**: The refresh rate for the data stream (optional).\n"
        "    - **data_key**: The key for the response data in the JSON file (optional).\n\n"
        "2. **CSV**\n"
        "    ```json\n"
        '    "processing": {\n'
        '        "delimiter": ",",\n'
        '        "header_line": 1,\n'
        '        "start_line": 2,\n'
        '        "comment_char": "#"\n'
        "    }\n"
        "    ```\n"
        "    - **delimiter**: The delimiter used in the CSV file (optional).\n"
        "    - **header_line**: The line number of the header in the CSV file (optional).\n"
        "    - **start_line**: The line number where the data starts in the CSV file (optional).\n"
        "    - **comment_char**: The character used for comments in the CSV file (optional).\n\n"
        "3. **TXT**\n"
        "    ```json\n"
        '    "processing": {\n'
        '        "delimiter": "\\t",\n'
        '        "header_line": 1,\n'
        '        "start_line": 2\n'
        "    }\n"
        "    ```\n"
        "    - **delimiter**: The delimiter used in the TXT file (optional).\n"
        "    - **header_line**: The line number of the header in the TXT file (optional).\n"
        "    - **start_line**: The line number where the data starts in the TXT file (optional).\n\n"
        "4. **JSON**\n"
        "    ```json\n"
        '    "processing": {\n'
        '        "info_key": "count",\n'
        '        "additional_key": "metadata",\n'
        '        "data_key": "results"\n'
        "    }\n"
        "    ```\n"
        "    - **info_key**: The key for additional information in the JSON file (optional).\n"
        "    - **additional_key**: An additional key in the JSON file (optional).\n"
        "    - **data_key**: The key for the response data in the JSON file (optional).\n\n"
        "5. **NetCDF**\n"
        "    ```json\n"
        '    "processing": {\n'
        '        "group": "group_name"\n'
        "    }\n"
        "    ```\n"
        "    - **group**: The group within the NetCDF file (optional).\n"
    ),
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
                    "example": {
                        "detail": (
                            "Error creating resource: <error message>"
                        )
                    }
                }
            }
        }
    }
)
async def create_url_resource(
    data: URLRequest,
    _: Dict[str, Any] = Depends(get_current_user)
):
    """
    Add a URL resource to CKAN.

    Parameters
    ----------
    data : URLRequest
        An object containing all the required parameters for creating a 
        URL resource.

    Returns
    -------
    dict
        A dictionary containing the ID of the created resource if 
        successful.

    Raises
    ------
    HTTPException
        If there is an error creating the resource, an HTTPException is 
        raised with a detailed message.
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
            processing=data.processing  # Optional processing
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
