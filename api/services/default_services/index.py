from fastapi import Request
from fastapi.templating import Jinja2Templates

from api.config import swagger_settings

def index(request: Request):
    templates = Jinja2Templates(directory="api/templates")
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": swagger_settings.swagger_title,
            "version": swagger_settings.swagger_version,
            "docs_url": f"{request.base_url}docs"}
    )

