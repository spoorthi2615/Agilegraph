from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.settings import settings
from app.api.v1.endpoints import health, upload, github
from app.api.routes import dashboard, analysis, graph, explainability
from app.core.exceptions import AgileGraphException, ValidationException, ResourceNotFoundException, EntityTooLargeException
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

    # Register Exception Handlers
    @app.exception_handler(ValidationException)
    async def validation_exception_handler(request: Request, exc: ValidationException):
        return JSONResponse(status_code=400, content={"detail": exc.message})
        
    @app.exception_handler(ResourceNotFoundException)
    async def not_found_exception_handler(request: Request, exc: ResourceNotFoundException):
        return JSONResponse(status_code=404, content={"detail": exc.message})
        
    @app.exception_handler(EntityTooLargeException)
    async def too_large_exception_handler(request: Request, exc: EntityTooLargeException):
        return JSONResponse(status_code=413, content={"detail": exc.message})
        
    @app.exception_handler(AgileGraphException)
    async def domain_exception_handler(request: Request, exc: AgileGraphException):
        return JSONResponse(status_code=500, content={"detail": exc.message})

    # Register Routers
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
    app.include_router(github.router, prefix="/api/v1", tags=["GitHub Import"])
    app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
    app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
    app.include_router(graph.router, prefix="/api/v1/graph", tags=["Graph"])
    app.include_router(explainability.router, prefix="/api/v1/explainability", tags=["Explainability"])
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
