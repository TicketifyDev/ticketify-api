from fastapi import FastAPI
from pathlib import Path
import sys

# Determine the parent directory of the current file.
parent_directory_resolved = Path(__file__).resolve().parents[1]

# Add the parent directory to the sys.path list to allow importing modules from that directory.
sys.path.append(str(parent_directory_resolved))

from scripts.create_initial_admin import check_initial_admin
from src.common.descriptions import tags_metadata
from src.endpoints import register, event_management, health_check, get_profile, login

app = FastAPI(
        title="Ticketify-API", 
        description="A comprehensive backend APIs for a ticket booking platform, designed to manage user authentication and authorization, event listings, ticket reservations, administrative functions and lot more.",
        version="1.0.0",
        openapi_tags=tags_metadata
    )

@app.get("/", include_in_schema=False)
async def read_root():
    return {"message": "Welcome to the Ticketify API!",
            "details": {
            "description": "A comprehensive backend APIs for a ticket booking platform, designed to manage user authentication and authorization, event listings, ticket reservations, administrative functions and lot more.",
            "documentation": "Visit `/docs` for the detailed API documentation and interactive testing or `/redoc` for the alternative documentation.",
            "version": "1.0.0",
            }
        }

@app.on_event("startup")
async def startup_event():
    check_initial_admin()

app.include_router(register.router)
app.include_router(login.router)
app.include_router(event_management.router)
app.include_router(health_check.router)
app.include_router(get_profile.router)
