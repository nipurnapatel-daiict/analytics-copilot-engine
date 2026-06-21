"""
Purpose: Define LangGraph workflow nodes with historical conversational awareness.
"""
from app.tools.sql_tool import sql_tool
from app.tools.rag_tool import rag_tool
from app.services.insight_service import InsightService
from app.graph.graph_router import GraphRouter
from app.llm.prompts import PROMPT_TEMPLATES
from app.llm.bedrock_client import get_bedrock_llm
from app.core.constants import ApplicationConstants

insight_service = InsightService()

def classifier_node(state: dict) -> dict:
    """Classifies query using context and blocks unauthorized write/structural operations."""

    context_text = state["query"]
    if state.get("history"):
        context_text = " ".join([m["content"] for m in state["history"][-2:]]) + " " + state["query"]
        
    query_lower = state["query"].lower().strip()
    
    if any(keyword in query_lower for keyword in ApplicationConstants.FORBIDDEN_SQL_KEYWORDS):
        state["route"] = "sql"  
        return state

    state["route"] = GraphRouter.classify_query(context_text)
    return state 


def sql_node(state: dict) -> dict:
    """Executes SQL query tool with robust read-only transaction exception boundaries."""
    from app.core.logger import logger
    from app.core.langfuse_client import langfuse_client
    
    execution_error = None
    response = {"result": [], "message": ""}
    
    span = langfuse_client.span(
        name="sql_node_execution",
        parent_trace_id=state.get("trace_id"),
        input={"question": state["query"]}
    )

    try:
        response = sql_tool.invoke({
            "question": state["query"],
            "trace_id": state.get("trace_id") 
        })
        
        tool_msg = str(response.get("message", "")).lower()
        if "read-only" in tool_msg or "readonly" in tool_msg or "cannot execute" in tool_msg:
            execution_error = (
                "Security Boundary Restriction: This analytics gateway is strictly READ-ONLY. "
                "Data modifications or structural changes (like DROP, INSERT, or ALTER) are prohibited."
            )

    except Exception as error:
        error_msg = str(error).lower()
        logger.error(f"SQL Tool Execution failed: {error}")
        
        if "read-only" in error_msg or "readonly" in error_msg or "cannot execute" in error_msg:
            logger.critical(f"SECURITY ALERT: Blocked unauthorized write/DROP attempt: {state['query']}")
            execution_error = (
                "Security Boundary Restriction: This analytics gateway is strictly READ-ONLY. "
                "Data modifications or structural changes (like DROP, INSERT, or ALTER) are prohibited."
            )
        else:
            execution_error = f"Database Tool Runtime Exception: {str(error)}"

    if execution_error:
        state["sql_response"] = []
        state["error"] = execution_error
        assistant_content = execution_error
        span.end(level="WARNING", status_message=execution_error)
    else:
        state["sql_response"] = response
        assistant_content = str(response.get("result", ""))
        span.end(output=response)

    if "history" not in state or state["history"] is None:
        state["history"] = []
        
    state["history"].append({"role": "user", "content": state["query"]})
    state["history"].append({"role": "assistant", "content": assistant_content})
    
    return state


def rag_node(state: dict) -> dict:
    """Retrieves context records from unstructured policy documents."""
    response_data = rag_tool.invoke({
        "query": state["query"], 
        "thread_id": state.get("thread_id"),
        "trace_id": state.get("trace_id")
    })
    
    new_thread_id = response_data.get("thread_id")

    return {
        **state,
        "rag_response": response_data,
        "thread_id": new_thread_id,
        "route": "rag"
    }


def hybrid_node(state: dict) -> dict:
    """Aggregates and synthesizes cross-domain relational insights."""
    
    sql_res = sql_tool.invoke({
        "question": state["query"],
        "trace_id": state.get("trace_id")
    })
    
    rag_res = rag_tool.invoke({
        "query": state["query"],
        "thread_id": state.get("thread_id"),
        "trace_id": state.get("trace_id")
    })
    
    state["sql_response"] = sql_res
    state["rag_response"] = rag_res
    state["final_response"] = insight_service.generate_hybrid_response(
        sql_response=sql_res,
        rag_response=rag_res
    )
    return state

def error_node(state: dict) -> dict:
    state["error"] = "Unable to classify query."
    return state


def summarize_node(state: dict) -> dict:
    """Synthesizes raw data dynamically based on semantic context routing."""
    from app.core.langfuse_client import langfuse_client
    span = langfuse_client.span(
        name="response_summarization",
        parent_trace_id=state.get("trace_id"),
        input=state.get("query")
    )

    try:
        route = state.get("route", "hybrid").lower().strip()
        if route not in PROMPT_TEMPLATES:
            route = "hybrid" 
        
        prompt = PROMPT_TEMPLATES[route].format(
            query=state.get("query"),
            sql_data=state.get("sql_response"),
            rag_data=state.get("rag_response"),
            hybrid_data=state.get("final_response")
        )

        llm = get_bedrock_llm()
        summary = llm.invoke(prompt).content.strip()

        state["final_response"] = summary
        span.end(output=summary)
        return state

    except Exception as error:
        span.end(level="ERROR", status_message=str(error))
        state["final_response"] = "Encountered an issue generating the final answer layout."
        return state

