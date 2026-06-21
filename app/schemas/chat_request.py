"""
Purpose: Store chat request schema.
"""
from typing import Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    thread_id: Optional[str] = None
