"""
Purpose: Manage PostgreSQL database operations.
"""

from sqlalchemy import text
from app.database.connection import engine
from app.core.logger import logger

class PostgresService:
    def execute_query(self, query: str):
        try:
            with engine.connect() as connection:
                result = connection.execute(text(query))
                rows = [dict(row._mapping) for row in result]
                logger.info("SQL query executed successfully.")
                return rows
        except Exception as error:
            logger.error(f"SQL query execution failed: {error}")
            raise Exception( "Failed to execute SQL query.")