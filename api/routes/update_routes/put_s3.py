from fastapi import APIRouter, HTTPException, status, Depends
from api.services import s3_services
from api.models.s3request_model import S3UpdateRequest
from tenacity import RetryError
from typing import Dict, Any

from api.services.keycloak_services.get_current_user import get_current_user

router = APIRouter()

@router.put(
    "/s3/{dataset_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update an S3 resource",
    description="Update an S3 resource and its associated metadata in the system.",
    responses={
        200: {
            "description": "S3 resource updated successfully",
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
                    "example": {"detail": "Error updating S3 resource: <error message>"}
                }
            }
        }
    }
)
async def update_s3_resource(
    dataset_id: str,
    data: S3UpdateRequest,
    _: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update an S3 resource and its associated metadata in the system.

    Parameters
    ----------
    dataset_id : str
        The ID of the dataset to be updated.
    data : S3UpdateRequest
        An object containing all the required parameters for updating an S3 resource.

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
        resource_id = s3_services.update_s3(
            dataset_id=dataset_id,
            resource_name=data.resource_name,
            resource_title=data.resource_title,
            owner_org=data.owner_org,
            resource_s3=data.resource_s3,
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
