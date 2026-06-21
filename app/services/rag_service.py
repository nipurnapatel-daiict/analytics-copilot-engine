"""
Purpose: Manage HTTP communications with the Milestone 02 RAG service.
"""

import requests
from app.core.config import settings
from app.core.logger import logger
from app.core.langfuse_client import langfuse_client

class RagService:

    def __init__(self):
        self.base_url = settings.RAG_API_BASE_URL.rstrip("/")

    def retrieve_response(self, query: str, thread_id: str = None, trace_id: str = None) -> dict:
        """Sends user prompt to the Milestone 02 API endpoint."""
        endpoint = self.base_url
        
        span = langfuse_client.span(
            name="rag_api_call", 
            parent_trace_id=trace_id, 
            input={"query": query, "thread_id": thread_id}
        )
        
        try:
            payload = {
                "query": query,
                "thread_id": thread_id
            }
            
            response = requests.post(
                endpoint,
                json=payload,
                timeout=getattr(settings, "AGENT_TIMEOUT", 30) 
            )
            response.raise_for_status()

            logger.info("RAG response retrieved successfully.")
            result = response.json()
            
            span.end(output=result)
            return result

        except Exception as error:
            logger.error(f"RAG API request failed on {endpoint}: {error}")
            span.end(level="ERROR", status_message=str(error))
            raise RuntimeError(f"Failed to retrieve RAG response: {error}")
    
    def get_all_threads(self) -> list:
        """Fetches historical conversation thread cards from Milestone 02."""
        endpoint = f"{self.base_url}/threads"
        try:
            response = requests.get(
                endpoint, 
                timeout=getattr(settings, "AGENT_TIMEOUT", 30)
            )
            response.raise_for_status()
            return response.json().get("threads", [])
        except Exception as error:
            logger.error(f"Failed to pull active sessions from Milestone 2: {error}")
            return []

