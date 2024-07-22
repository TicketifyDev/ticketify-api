from fastapi import FastAPI
from endpoints import login
from common.descriptions import tags_metadata
from endpoints import register, event_management, health_check, profile, update_profile

app = FastAPI(title="Ticketify-API", openapi_tags=tags_metadata)

app.include_router(register.router)
app.include_router(login.router)
app.include_router(event_management.router)
app.include_router(health_check.router)
app.include_router(profile.router)
app.include_router(update_profile.router)
