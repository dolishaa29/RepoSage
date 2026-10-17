import os

from fastapi import HTTPException
from langchain_aws import ChatBedrockConverse


# Claude on AWS Bedrock. AWS keys are read from .env by boto3 automatically
# (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY).
def get_llm() -> ChatBedrockConverse:
    model = os.getenv("BEDROCK_MODEL_ID")
    if not model:
        raise HTTPException(status_code=500, detail="AI is not set up: add BEDROCK_MODEL_ID to .env")
    return ChatBedrockConverse(model=model, region_name=os.getenv("AWS_REGION"), max_tokens=16000)
