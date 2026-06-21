"""
Purpose: Provide centralized Amazon Bedrock LLM client.
"""
from langchain_aws import ChatBedrock
from app.core.config import settings

def get_bedrock_llm():
    return ChatBedrock(
        model_id=settings.BEDROCK_MODEL_ID,
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        beta_use_converse_api=True,
    )