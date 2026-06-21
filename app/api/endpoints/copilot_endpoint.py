"""
Purpose: Expose analytics copilot API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.chat_request import ChatRequest
from app.schemas.chat_response import ChatResponse
from app.orchestration.copilot_service import CopilotService
from app.api.dependencies import get_copilot_service 
from app.services.opensearch_service import ChatHistoryService

router = APIRouter(prefix="/copilot", tags=["Analytics Copilot"])

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Health check endpoint that initializes OpenSearch index on first call."""
    try:
        chat_service = ChatHistoryService()
        chat_service.create_chat_index()
        return {"status": "healthy", "service": "analytics-copilot"}
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(error)}"
        )

@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat_with_copilot(
    request: ChatRequest,
    copilot_service: CopilotService = Depends(get_copilot_service)
):
    """
    Unified analytics copilot chat gateway routing queries to SQL, RAG, or Hybrid nodes.
    """
    try:
        response = copilot_service.process_query(
            query=request.query,
            thread_id=request.thread_id
        )
        return response
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error)
        )
        
        
@router.get("/threads", status_code=status.HTTP_200_OK)
def list_copilot_threads():
    """Retrieves conversation thread profiles directly from Milestone 2."""
    try:
        chat_service = ChatHistoryService()
        threads = chat_service.get_all_threads()
        
        sorted_threads = sorted(
            threads,
            key=lambda x: (x.get("timestamp") or "", x.get("thread_id") or ""),
            reverse=True
        )
        
        return {"status": "success", "threads": sorted_threads}
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Backend session mapping failed: {str(error)}"
        )


@router.get("/history/{thread_id}", status_code=status.HTTP_200_OK)
def get_copilot_thread_history(thread_id: str):
    """Retrieves message history for a specific thread from OpenSearch."""
    try:
        chat_service = ChatHistoryService()
        history = chat_service.get_thread_history(thread_id)
        return {"status": "success", "history": history}
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch thread history: {str(error)}"
        )


