from fastapi import Request
from fastapi.templating import Jinja2Templates

from api.config import swagger_settings
from api.services import status_services

def index(request: Request):
    templates = Jinja2Templates(directory="api/templates")
    
    # Verifica el estado de CKAN
    try:
        ckan_status = "CKAN is active" if status_services.check_ckan_status() else "CKAN is not reachable"
    except Exception as e:
        ckan_status = "CKAN not found."
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": swagger_settings.swagger_title,
            "version": swagger_settings.swagger_version,
            "docs_url": f"{request.base_url}docs",
            "ckan_status": ckan_status
        }
    )