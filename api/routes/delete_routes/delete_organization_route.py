from fastapi import APIRouter, HTTPException

from api.services import organization_services

router = APIRouter()

@router.delete(
    "/organization/{organization_name}",
    response_model=dict,
    summary="Delete an organization",
    description="Delete an organization from CKAN by its name, including all associated datasets and resources.",
    responses={
        200: {
            "description": "Organization deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Organization deleted successfully"}
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Error message explaining the bad request"}
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Organization not found"}
                }
            }
        }
    }
)
async def delete_organization(organization_name: str):
    """
    Endpoint to delete an organization in CKAN by its name.

    Parameters
    ----------
    organization_name : str
        The name of the organization to be deleted.

    Returns
    -------
    dict
        A message confirming the deletion of the organization.

    Raises
    ------
    HTTPException
        If there is an error deleting the organization, an HTTPException is raised with a detailed message.
    """
    try:
        organization_services.delete_organization(organization_name)
        return {"message": "Organization deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
