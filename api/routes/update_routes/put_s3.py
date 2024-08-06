from fastapi import APIRouter, HTTPException, status, Depends
from api.services.s3_services.update_s3 import update_s3
from api.models.update_s3_model import S3ResourceUpdateRequest
from typing import Dict, Any

from api.services.keycloak_services.get_current_user import get_current_user

router = APIRouter()

@router.put(
    "/s3/{resource_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update an existing S3 resource",
    description="""
Update an existing S3 resource and its associated metadata.

### Optional Fields
- **resource_name**: The unique name of the resource to be updated.
- **resource_title**: The title of the resource to be updated.
- **owner_org**: The ID of the organization to which the resource belongs.
- **resource_s3**: The S3 URL of the resource.
- **notes**: Additional notes about the resource.
- **extras**: Additional metadata to be updated or added to the resource.

### Example Payload
```json
{
    "resource_name": "updated_resource_name",
    "resource_s3": "http://new-s3-url.com/resource"
}
```
""",
    responses={
        200: {
        "description": "S3 resource updated successfully",
        "content": {
            "application/json": {
                "example": {"message": "S3 resource updated successfully"}
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
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "S3 resource not found"}
                }
            }
        }
    }
)
async def update_s3_resource(
    resource_id: str,
    data: S3ResourceUpdateRequest,
    _: Dict[str, Any] = Depends(get_current_user)):
    try:
        updated = await update_s3(
            resource_id=resource_id,
            resource_name=data.resource_name,
            resource_title=data.resource_title,
            owner_org=data.owner_org,
            resource_s3=data.resource_s3,
            notes=data.notes,
            extras=data.extras
        )
        if not updated:
            raise HTTPException(status_code=404, detail="S3 resource not found")
        return {"message": "S3 resource updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))