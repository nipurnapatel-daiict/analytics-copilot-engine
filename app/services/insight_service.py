"""
Purpose: Combine relational SQL results and unstructured RAG logs into a uniform payload.
"""

from app.core.logger import LoggerManager

logger = LoggerManager.get_logger()

class InsightService:

    def generate_hybrid_response(self, sql_response: list, rag_response: dict) -> dict:
        """Stitches structured database rows alongside knowledge base documents."""
        try:
            final_response = {
                "sql_insight": sql_response,
                "rag_insight": rag_response
            }
            logger.info("Hybrid insight dictionary built successfully.")
            return final_response

        except Exception as error:
            logger.error(f"Hybrid insight generation failed: {error}")
            raise RuntimeError("Failed to generate hybrid response payload.")