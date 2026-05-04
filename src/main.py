from fastapi import FastAPI
from src.router import router
from pathlib import Path
import sys
from contextlib import asynccontextmanager
from src.common.logging_config import logger

# Determine the parent directory of the current file.
parent_directory_resolved = Path(__file__).resolve().parents[1]

# Add the parent directory to the sys.path list to allow importing modules from that directory.
sys.path.append(str(parent_directory_resolved))

from scripts.create_initial_admin import check_initial_admin
from src.common.descriptions import tags_metadata

app = FastAPI(
        title="Ticketify-API", 
        description="A comprehensive backend APIs for a ticket booking platform, designed to manage user authentication and authorization, event listings, ticket reservations, administrative functions and lot more.",
        version="1.0.0",
        openapi_tags=tags_metadata
    )

@app.get("/", include_in_schema=False)
async def read_root():
    logger.info("Root endpoint '/' accessed.")
    return {"message": "Welcome to the Ticketify API!",
            "details": {
            "description": "A comprehensive backend APIs for a ticket booking platform, designed to manage user authentication and authorization, event listings, ticket reservations, administrative functions and lot more.",
            "documentation": "Visit `/docs` for the detailed API documentation and interactive testing or `/redoc` for the alternative documentation.",
            "version": "1.0.0",
            }
        }

@asynccontextmanager
async def startup_event(app: FastAPI):
    # Startup
    try :
        logger.info("Checking whether initial admin account exists or not.")
        await check_initial_admin()

    except Exception as e:
        logger.error("An error occurred during initial admin check: %s", e)
        raise e

app.include_router(router)
