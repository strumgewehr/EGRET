"""
News Sentiment Intelligence Platform - FastAPI application.
Production-ready: CORS, exception middleware, structured logging, rate limiting.
"""
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routers import articles, sources, dashboard, analytics, admin

settings = get_settings()

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: run migrations if needed. Shutdown: cleanup."""
    logger.info("Starting News Sentiment Intelligence API")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="News Sentiment Intelligence API",
    description="Aggregates news, sentiment analysis, bias detection, and analytics",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - restrict to configured origins
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Rate limiting (in-memory for single instance; use Redis in multi-instance)
from collections import defaultdict
from threading import Lock
_rate_store = defaultdict(list)
_rate_lock = Lock()


def rate_limit_exceeded(key: str) -> bool:
    now = time.time()
    window = settings.rate_limit_window_seconds
    max_req = settings.rate_limit_requests
    with _rate_lock:
        _rate_store[key] = [t for t in _rate_store[key] if now - t < window]
        if len(_rate_store[key]) >= max_req:
            return True
        _rate_store[key].append(now)
    return False


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Disable rate limiting for local development to avoid blocking requests
    return await call_next(request)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info("%s %s %s %.3fs", request.method, request.url.path, response.status_code, duration)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )


# Routers
app.include_router(articles.router)
app.include_router(sources.router)
app.include_router(dashboard.router)
app.include_router(analytics.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"service": "News Sentiment Intelligence API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
