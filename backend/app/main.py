from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.settings import settings
from app.api.v1.endpoints import health, upload, github
from app.core.logging import setup_logging
import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Sets up logging and logs application state transitions.
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.
    Registers middlewares and routers.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="AI-powered Post Quantum Cryptography Migration Platform",
        version=settings.VERSION,
        lifespan=lifespan,
    )

    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Routers
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
    app.include_router(github.router, prefix="/api/v1", tags=["GitHub Import"])

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
