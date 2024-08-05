from fastapi import APIRouter

from .put_kafka import router as put_kafka

router = APIRouter()

router.include_router(put_kafka)
