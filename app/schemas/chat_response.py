"""
Purpose: Store chat response schema.
"""
from typing import Any, Optional
from pydantic import BaseModel

class ChatResponse(BaseModel):
    thread_id: Optional[str]
    route: str
    response: Any
    timestamp: str
