from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from api.services import organization_services
from tenacity import RetryError

router = APIRouter()

@router.get(
    "/organization",
    response_model=List[str],
    summary="List all organizations",
    description="Retrieve a list of all organizations, with optional name filtering.",
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
                    "example": {
                        "detail": "Error message explaining the bad request"}
                }
            }
        }
    }
)
async def list_organizations(name: Optional[str] = Query(None, description="An optional string to filter organizations by name")):
    """
    Endpoint to list all organizations. Optionally, filter organizations by a partial name.

    Parameters
    ----------
    name : Optional[str]
        A string to filter organizations by name (case-insensitive).

    Returns
    -------
    List[str]
        A list of organization names, optionally filtered by the provided name.

    Raises
    ------
    HTTPException
        If there is an error retrieving the list of organizations, an HTTPException is raised with a detailed message.
    """
    try:
        organizations = organization_services.list_organization(name)
        return organizations
    except RetryError as e:
        final_exception = e.last_attempt.exception()
        raise HTTPException(status_code=400, detail=str(final_exception))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
