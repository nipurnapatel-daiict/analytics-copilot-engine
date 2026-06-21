"""
Purpose: Manage SQL agent operations and query generation.
"""
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import HumanMessage, SystemMessage
from app.database.connection import DATABASE_URL
from app.llm.bedrock_client import get_bedrock_llm
from app.core.constants import ApplicationConstants
from app.core.logger import logger
from app.core.langfuse_client import langfuse_client
import re

class SecurityError(Exception):
    """Raised when a forbidden or destructive SQL query structure is detected."""
    pass

class SQLAgentService:
    def __init__(self):
        self.database = SQLDatabase.from_uri(DATABASE_URL)
        self.llm = get_bedrock_llm()
        
        self.system_instruction = (
            "You are a PostgreSQL expert. Given an input question, create a syntactically correct PostgreSQL query to run.\n"
            "Return ONLY the raw SQL query string inside your response. Do NOT use markdown code blocks (```sql), formatting, or preambles.\n\n"
            "Only use the following table schemas:\n{table_info}"
        )

    def generate_query(self, question: str, trace_id: str = None) -> str:
        """Assembles schema context fragments to generate dialect-specific SQL."""
        span = langfuse_client.span(
            name="sql_generation", 
            parent_trace_id=trace_id, 
            input=question
        )
        try:
            system_message = SystemMessage(
                content=self.system_instruction.format(
                    table_info=self.database.get_table_info()
                )
            )
            human_message = HumanMessage(content=question)
            response = self.llm.invoke([system_message, human_message])

            query = response.content if hasattr(response, "content") else str(response)
            clean_query = query.replace("```sql", "").replace("```", "").strip()
            logger.info(f"Chain Input: {question}")
            logger.info("SQL query generated successfully.")
            span.end(output=clean_query)
            return clean_query
            
        except Exception as error:
            logger.error(f"SQL generation failed: {error}")
            span.end(level="ERROR", status_message=str(error))
            raise Exception(f"DEBUG: {str(error)}") 

    def validate_query(self, query: str) -> bool:
        """Enforces a strict deterministic read-only safety boundary using exact word checks."""
        normalized_query = query.lower().strip()

        if not normalized_query.startswith(ApplicationConstants.SELECT_KEYWORD):
            raise SecurityError("Unauthorized action: Only SELECT statements are allowed.")

        query_words = set(re.findall(r'\b[a-z]+\b', normalized_query))

        for keyword in ApplicationConstants.FORBIDDEN_SQL_KEYWORDS:
            if keyword in query_words:
                raise SecurityError(f"Forbidden data mutation keyword detected: '{keyword}'")

        return True