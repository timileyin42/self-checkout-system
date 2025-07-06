from fastapi import FastAPI
from app.api.v1.api_v1 import router as api_v1_router
from app.core.config import settings

def init_app(app: FastAPI):
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)
