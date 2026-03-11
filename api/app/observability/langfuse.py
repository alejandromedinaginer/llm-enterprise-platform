import logging
from functools import lru_cache
from langfuse import Langfuse
from app.core.settings import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_langfuse_client() -> Langfuse | None:
    settings = get_settings()
    if not settings.langfuse_secret_key or not settings.langfuse_public_key:
        logger.warning("Langfuse keys not configured, observability disabled.")
        return None
    try:
        return Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_base_url,
        )
    except Exception as exc:
        logger.warning(f"Failed to initialize Langfuse client: {exc}")
        return None


def create_chat_trace(trace_id: str, input_messages: list):
    settings = get_settings()
    client = get_langfuse_client()
    if client is None:
        return None
    try:
        return client.trace(
            id=trace_id,
            name="chat.completions",
            input=input_messages,
            metadata={"environment": settings.langfuse_environment},
        )
    except Exception as exc:
        logger.warning(f"Langfuse create_chat_trace failed: {exc}")
        return None


def create_llm_generation(trace, model: str, input_messages: list):
    settings = get_settings()
    if trace is None:
        return None
    try:
        return trace.generation(
            name="llm.generation",
            model=model,
            input=input_messages,
            metadata={"environment": settings.langfuse_environment},
        )
    except Exception as exc:
        logger.warning(f"Langfuse create_llm_generation failed: {exc}")
        return None


def update_chat_trace_success(trace, output: str, latency: float):
    if trace is None:
        return
    try:
        trace.update(output=output, metadata={"latency_seconds": latency})
    except Exception as exc:
        logger.warning(f"Langfuse update_chat_trace_success failed: {exc}")


def update_chat_trace_error(trace, error: str):
    if trace is None:
        return
    try:
        trace.update(metadata={"error": error})
    except Exception as exc:
        logger.warning(f"Langfuse update_chat_trace_error failed: {exc}")


def end_llm_generation_success(generation, output: str, usage: dict):
    if generation is None:
        return
    try:
        generation.end(output=output, usage=usage)
    except Exception as exc:
        logger.warning(f"Langfuse end_llm_generation_success failed: {exc}")


def end_llm_generation_error(generation, error: str):
    if generation is None:
        return
    try:
        generation.end(metadata={"error": error})
    except Exception as exc:
        logger.warning(f"Langfuse end_llm_generation_error failed: {exc}")


def flush_langfuse():
    client = get_langfuse_client()
    if client is None:
        return
    try:
        client.flush()
    except Exception as exc:
        logger.warning(f"Langfuse flush failed: {exc}")