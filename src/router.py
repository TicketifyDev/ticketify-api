from fastapi import APIRouter
from src.endpoints import event
from src.endpoints import (
    user,
    organizer,
    health_check,
    admin
)

router = APIRouter()

router.include_router(health_check.router)
router.include_router(user.router)
router.include_router(organizer.router)
router.include_router(event.router)
router.include_router(admin.router)
