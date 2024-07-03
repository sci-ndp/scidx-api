from fastapi import APIRouter
from .put_kafka import router as put_kafka_datasoruce_router
from .put_s3 import router as put_s3_datasource_router
from .put_url import router as put_url_datasource_router

router = APIRouter()

router.include_router(put_kafka_datasoruce_router)
router.include_router(put_s3_datasource_router)
router.include_router(put_url_datasource_router)

