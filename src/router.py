from fastapi import APIRouter
from src.endpoints import (
    register,
    login,
    event_management,
    health_check,
    get_profile,
    get_organizer_status,
    update_profile
)

router = APIRouter()

router.include_router(register.router)
router.include_router(login.router)
router.include_router(event_management.router)
router.include_router(health_check.router)
router.include_router(get_organizer_status.router)
router.include_router(get_profile.router)
router.include_router(update_profile.router)

