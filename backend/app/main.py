from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.settings import settings
from app.api.v1.endpoints import health, upload, github, metrics
from app.api.routes import dashboard, analysis, graph, explainability, report
from app.core.exceptions import AgileGraphException, ValidationException, ResourceNotFoundException, EntityTooLargeException
from app.core.logging import setup_logging, request_id_ctx
import logging
import uuid
import time
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
        expose_headers=["X-Request-ID"]
    )

    # Request Logging & Correlation ID Middleware
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        # Extract or generate correlation ID
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request_id_ctx.set(req_id)
        
        start_time = time.time()
        logger = logging.getLogger("app.middleware")
        
        # Avoid logging metrics endpoint noise
        is_health = request.url.path.startswith("/api/v1/health") or request.url.path.startswith("/api/v1/metrics")
        
        if not is_health:
            logger.info(f"Request started: {request.method} {request.url.path}")
            
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Request-ID"] = req_id
            
            # Update metrics store
            metrics.increment_request_metrics(response.status_code)
            
            if not is_health:
                logger.info(
                    f"Request completed: {request.method} {request.url.path} "
                    f"- Status: {response.status_code} - Duration: {process_time:.3f}s - Client: {request.client.host if request.client else 'unknown'}"
                )
            return response
        except Exception as e:
            process_time = time.time() - start_time
            metrics.increment_request_metrics(500)
            logger.error(
                f"Unhandled exception during {request.method} {request.url.path} "
                f"- Duration: {process_time:.3f}s",
                exc_info=True
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"},
                headers={"X-Request-ID": req_id}
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
    app.include_router(report.router, prefix="/api/v1/reports", tags=["Reports"])
    app.include_router(metrics.router, prefix="/api/v1", tags=["Operational"])
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
