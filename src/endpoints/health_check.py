from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Health Check"])

@router.get("/health-check")
async def health_check():
    """
    API to check whether the web server is up or down.
    """
    return JSONResponse(content={"status":"Server is up and running"},status_code=200)
