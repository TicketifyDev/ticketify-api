from fastapi import FastAPI
from endpoints import get_profile, login
from common.descriptions import tags_metadata
from endpoints import register, event_management, health_check
from endpoints.admin_management import pending_organizer_requests

app = FastAPI(title="Ticketify-API", openapi_tags=tags_metadata)

app.include_router(register.router)
app.include_router(login.router)
app.include_router(event_management.router)
app.include_router(health_check.router)
app.include_router(get_profile.router)
app.include_router(pending_organizer_requests.router)