from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.config import settings
from app.routers import auth, portfolios, networth, export
from app.services.scheduler_service import scheduler_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting WealthWise API")
    scheduler_service.start()
    yield
    # Shutdown
    logger.info("Shutting down WealthWise API")
    scheduler_service.shutdown()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="WealthWise - Personal Portfolio Management API",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.vite_api_base_url, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(portfolios.router)
app.include_router(networth.router)
app.include_router(export.router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "WealthWise API is running",
        "version": settings.app_version,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "scheduler_running": scheduler_service.scheduler.running,
        "version": settings.app_version
    }
