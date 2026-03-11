"""LLM endpoints with OpenAI-compatible contracts."""

from typing import Any, Literal

from fastapi import APIRouter, Query

from app.schemas.chat import ChatCompletionRequestSchema
from app.services import llm_service

router = APIRouter(prefix="/v1", tags=["LLM"])


@router.get("/models")
def list_models(
    base_url: str = Query(..., min_length=1, description="Base URL del proveedor."),
    provider: Literal["vllm", "ollama"] | None = Query(None),
) -> dict[str, Any]:
    return llm_service.list_models(base_url=base_url.strip(), provider=provider)


@router.post("/chat/completions")
def create_chat_completion(payload: ChatCompletionRequestSchema) -> dict[str, Any]:
    request = payload.to_domain()
    return llm_service.create_chat_completion(request)