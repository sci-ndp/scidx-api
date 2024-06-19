from fastapi import APIRouter

from .post_datasource import router as post_datasoruce_router
from .post_kafka import router as post_kafka_datasoruce_router
from .post_organization import router as post_organization_router

router = APIRouter()

router.include_router(post_datasoruce_router)
router.include_router(post_kafka_datasoruce_router)
router.include_router(post_organization_router)
