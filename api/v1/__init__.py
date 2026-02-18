from fastapi import APIRouter
from api.v1.routers import (
    screenshots
)

router = APIRouter()
router.include_router(screenshots.router, prefix="/screenshots")
