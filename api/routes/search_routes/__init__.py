from fastapi import APIRouter

from .search_datasource_route import router as get_router
from .list_organizations_route import router as list_organizations_router
from .get_stream import router as get_stream_router
from ...config import swagger_settings

router = APIRouter()

router.include_router(get_router)
router.include_router(list_organizations_router)
if not swagger_settings.pop:
    router.include_router(get_stream_router)
