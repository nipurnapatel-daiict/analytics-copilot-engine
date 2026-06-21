"""
Purpose: Initialize FastAPI application.
"""
from fastapi import FastAPI
from app.api.routers import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def health_check():
    """Application level network connectivity testing hook."""
    return {"message": "Analytics Copilot API Running"}