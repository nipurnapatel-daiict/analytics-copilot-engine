"""
Purpose: Register application API routes.
"""
from fastapi import APIRouter
from app.api.endpoints.copilot_endpoint import router as copilot_router

api_router = APIRouter()
api_router.include_router(copilot_router)