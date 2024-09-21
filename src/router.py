from fastapi import APIRouter
from src.endpoints import (
    user,
    organizer,
    event_management,
    health_check
)

router = APIRouter()

router.include_router(health_check.router)
router.include_router(user.router)
router.include_router(organizer.router)
router.include_router(event_management.router)

