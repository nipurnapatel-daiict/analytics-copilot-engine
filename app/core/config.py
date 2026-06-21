"""
Purpose: Store centralized application configuration.
"""

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)
from typing import Optional
import os 

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    ENVIRONMENT: str

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str

    BEDROCK_MODEL_ID: str
    EMBEDDING_MODEL: str

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    OPENSEARCH_HOST: str
    OPENSEARCH_PORT: int
    OPENSEARCH_INDEX: str
    
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_SECRET_KEY: str 
    LANGFUSE_HOST : str = "https://langfuse.armakuni.in"


    RAG_API_BASE_URL: str
    AGENT_TIMEOUT: int = 30


    MAX_GRAPH_ITERATIONS: int

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()

