from fastapi import APIRouter

from .post import router as post_router
from .get import router as get_router

router = APIRouter()

router.include_router(post_router)
router.include_router(get_router)
