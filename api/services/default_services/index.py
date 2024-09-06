from fastapi import Request
from fastapi.templating import Jinja2Templates

from api.config import swagger_settings
from api.services import status_services

from api.services.keycloak_services.introspect_user_token import get_client_token


def index(request: Request):
    templates = Jinja2Templates(directory="api/templates")
    
    # Check CKAN status
    try:
        ckan_is_active = status_services.check_ckan_status()
        
        # Check Keycloak status by attempting to get a client token
        try:
            get_client_token()  # If this succeeds, Keycloak is reachable
            keycloak_is_active = True
        except Exception as e:
            keycloak_is_active = False

        # Determine the status message based on CKAN and Keycloak statuses
        if ckan_is_active and keycloak_is_active:
            status = "CKAN and Keycloak are active and reachable."
        else:
            if ckan_is_active and not keycloak_is_active:
                status = "CKAN is active, but Keycloak is not reachable."
            elif keycloak_is_active:
                status = "Keycloak is active, but CKAN is not reachable."
            else:
                status = "CKAN and Keycloak are not reachable."
    except Exception as e:
        status = "CKAN and Keycloak are not reachable."
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": swagger_settings.swagger_title,
            "version": swagger_settings.swagger_version,
            "docs_url": f"{request.base_url}docs",
            "status": status
        }
    )
    