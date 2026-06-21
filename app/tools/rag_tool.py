"""
Purpose: Provide a compliant LangChain tool wrapper for the RAG service.
"""
from typing import Optional
from langchain.tools import tool
from app.services.rag_service import RagService

rag_client = RagService()

@tool("rag_tool")
def rag_tool(query: str, thread_id: Optional[str] = None, trace_id: Optional[str] = None) -> dict:
    """
    Retrieve contextual enterprise information, company documentation, 
    policies, and unstructured knowledge base records.
    """
    return rag_client.retrieve_response(query=query, thread_id=thread_id, trace_id=trace_id)