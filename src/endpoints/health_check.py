from fastapi import APIRouter
from fastapi.responses import JSONResponse
from src.common.logging_config import logger

router = APIRouter(prefix="/api/v1", tags=["Health Check"])

@router.get("/health-check")
async def health_check():
    """
    API to check whether the web server is up or down.
    """
    logger.info("Health check endpoint accessed.")
    return JSONResponse(content={"status":"Server is up and running"},status_code=200)
