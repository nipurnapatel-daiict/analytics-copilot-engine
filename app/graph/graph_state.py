"""
Purpose: Store workflow state for LangGraph execution.
"""
from typing import TypedDict, Optional, Any

class GraphState(TypedDict):
    query: str
    thread_id: Optional[str]
    route: Optional[str]
    sql_response: Optional[Any]
    rag_response: Optional[Any]
    final_response: Optional[Any]
    error: Optional[str]
    trace_id: Optional[str]
