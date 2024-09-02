from fastapi import FastAPI
from src.common.descriptions import tags_metadata
from src.router import router

app = FastAPI(title="Ticketify-API", openapi_tags=tags_metadata)

app.include_router(router)
