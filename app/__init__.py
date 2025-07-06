from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core import setup_logging
from .core.config import settings
from .api import init_app as init_api
from .utils.middleware import request_middleware
from .db.session import session_manager

def create_application() -> FastAPI:
    # Initialize logging first
    setup_logging()
    
    # Create FastAPI instance
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    @app.get("/")
    def root():
        return {"message": "Self-checkout API is running", "version": settings.APP_VERSION}

    @app.get("/health", tags=["System"])
    def health_check():
        return {"status": "healthy"}

    # metrics route
    @app.get("/metrics", tags=["System"])
    def metrics():
        return {
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "debug": settings.DEBUG
        }

    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom middleware
    app.middleware("http")(request_middleware)
    
    # Initialize API routes
    init_api(app)
    
    # Database lifecycle events
    @app.on_event("startup")
    async def startup():
        session_manager.init(settings.DATABASE_URL)
        
    @app.on_event("shutdown")
    async def shutdown():
        await session_manager.close()
    
    return app

app = create_application()
