"""
Purpose: Store reusable API dependencies.
"""
from app.orchestration.copilot_service import CopilotService

def get_copilot_service() -> CopilotService:
    """Dependency provider factory for clean resource lifecycle management."""
    return CopilotService()