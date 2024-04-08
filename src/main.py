from fastapi import FastAPI
from auth import register
from common.descriptions import tags_metadata

app = FastAPI(title="Ticketify-API", openapi_tags=tags_metadata)

app.include_router(register.router)


