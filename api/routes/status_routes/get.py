from fastapi import APIRouter, HTTPException
from api.services import status_services

router = APIRouter()

@router.get(
    "/",
    response_model=str,
    summary="Check CKAN status",
    description="Check if the CKAN server is active and reachable."
)
async def get_ckan_status():
    """
    Endpoint to check if CKAN is active and reachable.

    Returns
    -------
    str
        A message confirming if CKAN is active.

    Raises
    ------
    HTTPException
        If there is an error connecting to CKAN, an HTTPException is raised with a detailed message.
    """
    try:
        is_active = status_services.check_ckan_status()
        if is_active:
            return "CKAN is active and reachable."
        else:
            raise HTTPException(status_code=503, detail="CKAN is not reachable.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
