from fastapi import APIRouter
from .put_kafka import router as put_kafka_datasoruce_router

router = APIRouter()

router.include_router(put_kafka_datasoruce_router)
