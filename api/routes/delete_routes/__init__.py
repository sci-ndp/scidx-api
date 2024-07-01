from fastapi import APIRouter

from .delete_organization_route import router as delete_organization_router

router = APIRouter()

router.include_router(delete_organization_router)
