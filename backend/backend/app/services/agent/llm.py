"""LangChain LLM with confidence guardrails for agent tools."""

import logging
import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Last Minute Life Saver, an autonomous productivity assistant.
You help users manage calendar conflicts, approaching deadlines, and meeting prep.
Be concise, actionable, and honest about uncertainty.
Never invent calendar events or tasks that were not provided in context.
If you are unsure, say so and suggest what information you need."""


def _estimate_confidence(response: str, context: str) -> float:
    """Heuristic confidence score based on hedging language and context overlap."""
    hedging = ["maybe", "perhaps", "not sure", "i think", "possibly", "might"]
    lower = response.lower()
    penalty = sum(0.08 for h in hedging if h in lower)

    context_words = set(re.findall(r"\w+", context.lower()))
    response_words = set(re.findall(r"\w+", lower))
    overlap = len(context_words & response_words) / max(len(context_words), 1)
    base = 0.5 + min(overlap * 0.4, 0.4)

    return round(max(0.1, min(1.0, base - penalty)), 2)


def _fallback_response(user_message: str) -> dict[str, Any]:
    return {
        "reply": (
            "I'm running in offline mode (no API key configured). "
            "Based on your request, I recommend checking your calendar for conflicts "
            "and reviewing tasks sorted by due date. "
            f"Your message: {user_message[:200]}"
        ),
        "confidence": 0.5,
        "model": "fallback",
        "fallback": True,
    }


def get_chat_model() -> ChatOpenAI | None:
    """Return LangChain chat model when API key is configured."""
    settings = get_settings()
    if not settings.openai_api_key:
        return None

    if settings.openai_api_base and "your-resource" in settings.openai_api_base:
        logger.warning("Placeholder OpenAI API base URL detected; the LLM will fall back to offline mode.")
        return None

    kwargs: dict[str, Any] = {
        "api_key": settings.openai_api_key,
        "model": settings.openai_model,
        "temperature": settings.openai_temperature,
        "max_retries": settings.openai_max_retries,
    }
    if settings.openai_api_base:
        kwargs["base_url"] = settings.openai_api_base

    return ChatOpenAI(**kwargs)


def chat(user_message: str, context: str = "") -> dict[str, Any]:
    """Invoke LLM with guardrails; falls back gracefully without API key."""
    model = get_chat_model()
    if not model:
        return _fallback_response(user_message)

    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    if context:
        messages.append(SystemMessage(content=f"Context:\n{context}"))
    messages.append(HumanMessage(content=user_message))

    try:
        response = model.invoke(messages)
        content = response.content if isinstance(response.content, str) else str(response.content)
        confidence = _estimate_confidence(content, context)
        settings = get_settings()

        if confidence < settings.llm_confidence_threshold:
            content = (
                f"{content}\n\n"
                f"[Note: Confidence {confidence:.0%} — please verify before acting.]"
            )

        return {
            "reply": content,
            "confidence": confidence,
            "model": settings.openai_model,
            "fallback": False,
        }
    except Exception as exc:
        logger.error("LangChain LLM call failed: %s", exc)
        return _fallback_response(user_message)


def draft_email(purpose: str, recipient: str, context: str) -> dict[str, Any]:
    """Draft a professional email via the LLM."""
    prompt = (
        f"Draft a professional email for: {purpose}\n"
        f"Recipient: {recipient}\n"
        f"Context: {context}\n"
        "Keep it concise and polite."
    )
    return chat(prompt, context=context)
