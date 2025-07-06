from fastapi import FastAPI
from app.api.v1.api_v1 import router as api_v1_router
from app.db.session import session_manager
from app.core.config import settings

def init_app(app: FastAPI):
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)
    
    @app.on_event("startup")
    async def startup():
        session_manager.init(settings.DATABASE_URL)
        
    @app.on_event("shutdown")
    async def shutdown():
        await session_manager.close()
