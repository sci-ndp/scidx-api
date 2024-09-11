from fastapi import APIRouter

from .post_datasource import router as post_datasoruce_router
from .post_kafka import router as post_kafka_datasoruce_router
from .post_organization import router as post_organization_router
from .post_url import router as post_url_router
from .post_s3 import router as post_s3_router
from .post_stream import router as post_stream_router
from ...config import swagger_settings

router = APIRouter()

# router.include_router(post_datasoruce_router)
router.include_router(post_kafka_datasoruce_router)
router.include_router(post_organization_router)
router.include_router(post_url_router)
router.include_router(post_s3_router)
if not swagger_settings.pop:
    router.include_router(post_stream_router)

