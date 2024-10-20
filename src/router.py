from fastapi import APIRouter
from src.endpoints import (
    health_check,
    user,
    organizer,
    health_check,
    event,
    admin
)

router = APIRouter()

router.include_router(health_check.router)
router.include_router(admin.router)
router.include_router(user.router)
router.include_router(organizer.router)
router.include_router(event.router)

