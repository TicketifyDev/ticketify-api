from fastapi import FastAPI
from auth import register,login
from common.descriptions import tags_metadata
from endpoints import event_management,health_check

app = FastAPI(title="Ticketify-API", openapi_tags=tags_metadata)

app.include_router(register.router)
app.include_router(login.router)
app.include_router(event_management.router)
app.include_router(health_check.router)
