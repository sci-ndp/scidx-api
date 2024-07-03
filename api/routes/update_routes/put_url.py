from fastapi import APIRouter, HTTPException, status, Depends
from api.services import url_services
from api.models.urlrequest_model import URLUpdateRequest
from tenacity import RetryError
from typing import Dict, Any

from api.services.keycloak_services.get_current_user import get_current_user

router = APIRouter()

@router.put(
    "/url/{dataset_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update a URL resource",
    description="Update a URL resource and its associated metadata in the system.",
    responses={
        200: {
            "description": "URL resource updated successfully",
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
                    "example": {"detail": "Error updating URL resource: <error message>"}
                }
            }
        }
    }
)
async def update_url_resource(
    dataset_id: str,
    data: URLUpdateRequest,
    _: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update a URL resource and its associated metadata in the system.

    Parameters
    ----------
    dataset_id : str
        The ID of the dataset to be updated.
    data : URLUpdateRequest
        An object containing all the required parameters for updating a URL resource.

    Returns
    -------
    dict
        A dictionary containing the ID of the updated resource if successful.

    Raises
    ------
    HTTPException
        If there is an error updating the resource, an HTTPException is raised with a detailed message.
    """
    try:
        resource_id = url_services.update_url(
            dataset_id=dataset_id,
            resource_name=data.resource_name,
            resource_title=data.resource_title,
            owner_org=data.owner_org,
            resource_url=data.resource_url,
            notes=data.notes,
            extras=data.extras
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
