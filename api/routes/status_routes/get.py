from fastapi import APIRouter, HTTPException
from api.services import status_services
from api.services.keycloak_services.get_admin_token import get_admin_token

router = APIRouter()

@router.get(
    "/",
    response_model=str,
    summary="Check system status",
    description="Check if the CKAN and Keycloak servers are active and reachable."
)
async def get_status():
    """
    Endpoint to check if CKAN and Keycloak are active and reachable.

    Returns
    -------
    str
        A message confirming if CKAN and Keycloak are active.

    Raises
    ------
    HTTPException
        If there is an error connecting to CKAN or Keycloak, an HTTPException is raised with a detailed message.
    """
    try:
        ckan_is_active = status_services.check_ckan_status()
        try:
            keycloak_is_active = get_admin_token()
        except Exception as e:
            keycloak_is_active = False
        if ckan_is_active and keycloak_is_active:
            return "CKAN and Keycloak are active and reachable."
        else:
            if ckan_is_active and not keycloak_is_active:
                raise HTTPException(status_code=503, detail="Keycloak is not reachable.")
            elif keycloak_is_active:
                raise HTTPException(status_code=503, detail="CKAN is not reachable.")
            else:
                raise HTTPException(status_code=503, detail="CKAN and Keycloak are not reachable.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
