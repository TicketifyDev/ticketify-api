import uvicorn
from src.main import app
from src.common.logging_config import logger

if __name__ == "__main__":
    try:
        logger.info("Starting the application...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logger.info("Application has stopped.")
    