from fastapi import status, APIRouter
from src.common.utils import response_content
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v1", tags=["Health Check"])

@router.get("/health-check")
async def health_check():
    """
    API to check whether the web server is up or down.
    """
    return JSONResponse(
        content=response_content(
            200,
            "Server is up and running",  
        ),
        status_code=status.HTTP_200_OK
    )
