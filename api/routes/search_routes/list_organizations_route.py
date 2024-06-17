from fastapi import APIRouter, HTTPException
from typing import List
from api.services import organization_services

router = APIRouter()

@router.get(
    "/organization",
    response_model=List[str],
    summary="List all organizations",
    description="Retrieve a list of all organizations in CKAN.",
    responses={
        200: {
            "description": "A list of all organizations",
            "content": {
                "application/json": {
                    "example": ["org1", "org2", "org3"]
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
        }
    }
)
async def list_organizations():
    """
    Endpoint to list all organizations in CKAN.

    Returns
    -------
    List[str]
        A list of organization names.

    Raises
    ------
    HTTPException
        If there is an error retrieving the list of organizations, an HTTPException is raised with a detailed message.
    """
    try:
        organizations = organization_services.list_organization()
        return organizations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
