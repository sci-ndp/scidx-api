from fastapi import APIRouter, HTTPException, status, Depends
from api.services.url_services.update_url import update_url
from api.models.update_url_model import URLUpdateRequest
from tenacity import RetryError
from typing import Dict, Any

from api.services.keycloak_services.get_current_user import get_current_user

router = APIRouter()

@router.put(
    "/url/{resource_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update an existing URL resource",
    description="""
Update an existing URL resource in CKAN.

### Common Fields for All File Types
- **resource_name**: The unique name of the resource.
- **resource_title**: The title of the resource.
- **owner_org**: The ID of the organization to which the resource belongs.
- **resource_url**: The URL of the resource.
- **file_type**: The type of the file (`stream`, `CSV`, `TXT`, `JSON`, `NetCDF`).
- **notes**: Additional notes about the resource (optional).
- **extras**: Additional metadata to be added to the resource package as extras (optional).
- **mapping**: Mapping information for the dataset (optional).
- **processing**: Processing information for the dataset, which varies based on the `file_type`.

### Example Payload
```json
{
    "resource_name": "example_resource_name",
    "resource_title": "Example Resource Title",
    "owner_org": "example_org_id",
    "resource_url": "http://example.com/resource",
    "file_type": "CSV",
    "notes": "Additional notes about the resource.",
    "extras": {"key1": "value1", "key2": "value2"},
    "mapping": {"field1": "mapping1", "field2": "mapping2"},
    "processing": {"delimiter": ",", "header_line": 1, "start_line": 2, "comment_char": "#"}
}
""",
    responses={
        200: {
            "description": "Resource updated successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Resource updated successfully"}
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Error updating resource: <error message>"}
                }
            }
        }
    }
)
async def update_url_resource(
    resource_id: str,
    data: URLUpdateRequest,
    _: Dict[str, Any] = Depends(get_current_user)):
    """
    Update an existing URL resource in CKAN.

    Parameters
    ----------
    resource_id : str
        The ID of the resource to be updated.
    data : URLUpdateRequest
        An object containing all the parameters for updating a URL resource.

    Returns
    -------
    dict
        A dictionary containing the message if successful.

    Raises
    ------
    HTTPException
        If there is an error updating the resource, an HTTPException is raised with a detailed message.
    """
    try:
        await update_url(
            resource_id=resource_id,
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
        return {"message": "Resource updated successfully"}
    except RetryError as e:
        final_exception = e.last_attempt.exception()
        raise HTTPException(status_code=400, detail=str(final_exception))
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Reserved key error: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
