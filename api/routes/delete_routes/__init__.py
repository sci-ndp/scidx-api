from fastapi import APIRouter

from .delete_organization_route import router as delete_organization_router
from .delete_kafka import router as delete_kafka_router

router = APIRouter()

router.include_router(delete_organization_router)
router.include_router(delete_kafka_router)
