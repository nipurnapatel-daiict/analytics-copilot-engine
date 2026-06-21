"""
Purpose: Orchestrate analytics copilot workflow execution with proper checkpointer parameters.
"""
from datetime import datetime, timezone
from app.graph.graph_builder import GraphBuilder
from app.graph.memory import MemoryManager
from app.services.opensearch_service import ChatHistoryService
from app.core.logger import logger
from fastapi import HTTPException
from app.core.langfuse_client import langfuse_client

class CopilotService:

    def __init__(self):
        self.graph = GraphBuilder.build_graph()
        self.chat_service = ChatHistoryService()
        self.chat_service.create_chat_index()

    def process_query(self, query: str, thread_id: str = None):
        trace = langfuse_client.trace(
            name="copilot_orchestration",
            session_id=thread_id,
            input={"query": query},
            tags=["milestone-03-analytics-copilot"] 
        )
        try:
            config_id = thread_id if thread_id else "new-session-placeholder"
            config = {"configurable": {"thread_id": config_id}}

            response = self.graph.invoke(
                {
                    "query": query,
                    "thread_id": thread_id, 
                    "trace_id": trace.id
                },
                config=config  
            )

            actual_thread_id = response.get("thread_id") or thread_id or "new-session"
             
            final_response = (
                response.get("final_response")
                or response.get("sql_response")
                or response.get("rag_response")
                or response.get("error")
            )

            external_timestamp = response.get("timestamp") or datetime.now(timezone.utc).isoformat()
            
            self.chat_service.save_message(
                thread_id=actual_thread_id,
                query=query,
                response=final_response,
                route=response.get("route", "error")
            )

            logger.info(f"Workflow executed for thread: {actual_thread_id}")
            trace.update(output=final_response) 
            
            return {
                "thread_id": actual_thread_id,
                "route": response.get("route", "error"),
                "response": final_response,
                "timestamp": external_timestamp
            }
           
        except Exception as error:
            logger.error(f"Copilot workflow failed: {error}")
            trace.update(level="ERROR", status_message=str(error))
            raise HTTPException(status_code=500, detail=f"Debug Error: {str(error)}")
