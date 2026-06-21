"""
Purpose: Provide SQL analytics tool for LangGraph workflows with error boundary catching.
"""
from langchain.tools import tool
from app.services.postgres_service import PostgresService
from app.services.sql_agent_service import SQLAgentService

postgres_service = PostgresService()
sql_agent_service = SQLAgentService()

@tool("sql_analytics_tool")
def sql_tool(question: str, trace_id: str = None) -> dict:
    """
    Execute analytical SQL queries safely against the analytical warehouse database.
    """
    try:
        generated_query = sql_agent_service.generate_query(question, trace_id=trace_id)
        sql_agent_service.validate_query(generated_query)
        result = postgres_service.execute_query(generated_query)

        return {
            "query": generated_query,
            "result": result,
            "status": "success",
        }
    except Exception as err:
        return {
            "query": locals().get("generated_query", "Failed generation"),
            "result": f"Database execution error: {str(err)}",
            "status": "error"
        }