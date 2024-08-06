from fastapi import APIRouter

from .put_kafka import router as put_kafka
from .put_url import router as put_url
from .put_s3 import router as put_s3

router = APIRouter()

router.include_router(put_kafka)
router.include_router(put_url)
router.include_router(put_s3)
