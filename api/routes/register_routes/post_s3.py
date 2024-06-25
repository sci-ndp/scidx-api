from fastapi import APIRouter, HTTPException, status, Depends

from api.services.keycloak_services.get_current_user import get_current_user
from api.services.s3_services.add_s3 import add_s3
from api.models.s3request_model import S3Request

router = APIRouter()


@router.post(
    "/s3",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new S3 resource",
    description="Create a new URL resource.",
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
async def create_s3_resource(
    data: S3Request,
    # _=Depends(get_current_user)
):
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
        resource_id = add_s3(
            resource_name=data.resource_name,
            resource_title=data.resource_title,
            owner_org=data.owner_org,
            resource_s3=data.resource_s3,
            notes=data.notes
        )
        return {"id": resource_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
