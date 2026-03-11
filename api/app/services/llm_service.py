import time
import uuid
from typing import Any
from openai import APIConnectionError, APIError, APITimeoutError
from app.agents.chat_agent import run_chat_agent
from app.clients.openai_client import get_openai_client
from app.core.exceptions import UpstreamServiceError
from app.models.chat import ChatRequest
from app.observability.langfuse import (
    create_chat_trace,
    update_chat_trace_success,
    update_chat_trace_error,
)


def list_models() -> dict[str, Any]:
    client = get_openai_client()
    try:
        response = client.models.list()
    except (APIConnectionError, APITimeoutError, APIError) as exc:
        raise UpstreamServiceError(f"Error listing models from upstream provider: {exc}") from exc
    return response.model_dump(mode="json")


def create_chat_completion(request: ChatRequest) -> dict[str, Any]:
    trace_id = str(uuid.uuid4())
    input_messages = [{"role": m.role, "content": m.content} for m in request.messages]
    trace = create_chat_trace(trace_id, input_messages)
    start = time.time()

    try:
        result = run_chat_agent(request, trace=trace)
        latency = time.time() - start
        output = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        update_chat_trace_success(trace, output, latency)
        return result
    except (APIConnectionError, APITimeoutError, APIError) as exc:
        update_chat_trace_error(trace, str(exc))
        raise UpstreamServiceError(f"Error generating chat completion from upstream provider: {exc}") from exc