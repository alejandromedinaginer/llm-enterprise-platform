from typing import Any
from fastapi import APIRouter
from app.schemas.chat import ChatCompletionRequestSchema
from app.services import llm_service

router = APIRouter(prefix="/v1", tags=["LLM"])


@router.get("/models")
def list_models() -> dict[str, Any]:
    return llm_service.list_models()


@router.post("/chat/completions")
def create_chat_completion(payload: ChatCompletionRequestSchema) -> dict[str, Any]:
    request = payload.to_domain()
    return llm_service.create_chat_completion(request)