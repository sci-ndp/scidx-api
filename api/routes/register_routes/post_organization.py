from fastapi import APIRouter, HTTPException, status, Depends
from api.models import OrganizationRequest
from api.services import organization_services
from tenacity import RetryError
from typing import Dict, Any
from api.services.keycloak_services.get_current_user import get_current_user

router = APIRouter()

@router.post(
    "/organization",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new organization",
    description=(
        "Create a new organization with the given name, title, "
        "and description."
    ),
    responses={
        201: {
            "description": "Organization created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "305284e6-6338-4e13-b39b-e6efe9f1c45a",
                        "message": "Organization created successfully",
                    }
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Organization name already exists."
                    }
                }
            }
        }
    }
)
async def create_organization_endpoint(
    org: OrganizationRequest,
    _: Dict[str, Any] = Depends(get_current_user)
):
    """
    Endpoint to create a new organization in CKAN.

    Parameters
    ----------
    org : OrganizationRequest
        An object containing the name, title, and description of 
        the organization.

    Returns
    -------
    dict
        A dictionary containing the ID of the created organization 
        and a success message.

    Raises
    ------
    HTTPException
        If there is an error creating the organization, an 
        HTTPException is raised with a detailed message.
    """
    try:
        organization_id = organization_services.create_organization(
            name=org.name,
            title=org.title,
            description=org.description,
        )
        return {
            "id": organization_id,
            "message": "Organization created successfully",
        }
    except RetryError as e:
        final_exception = e.last_attempt.exception()
        error_message = str(final_exception)
        if "Group name already exists in database" in error_message:
            raise HTTPException(
                status_code=400, 
                detail="Organization name already exists."
            )
        elif "Validation error" in error_message:
            raise HTTPException(
                status_code=400, 
                detail=f"Validation error: {error_message}"
            )
        elif "CKAN API endpoint not found" in error_message:
            raise HTTPException(
                status_code=404, 
                detail="CKAN API endpoint not found"
            )
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unexpected error: {error_message}"
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
