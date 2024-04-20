from fastapi import APIRouter

router = APIRouter(tags=["Health Check"])

@router.get("/health-check")
async def health_check():
    """
    API to check whether the web server is up or down.
    """
    return {
            "message":"Server is up and running",
            "statusCode": 200,
            "errorCode": None
        }
