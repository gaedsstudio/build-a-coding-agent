from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def chat(messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Call an OpenAI-compatible /chat/completions endpoint using only stdlib."""
    api_key = os.environ.get("AGENT_API_KEY")
    model = os.environ.get("AGENT_MODEL")
    base_url = os.environ.get("AGENT_BASE_URL", "https://api.openai.com/v1").rstrip("/")

    if not api_key:
        raise RuntimeError("Set AGENT_API_KEY first.")
    if not model:
        raise RuntimeError("Set AGENT_MODEL first.")

    payload: dict[str, Any] = {"model": model, "messages": messages}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LLM request failed ({exc.code}): {detail}") from exc

    return body["choices"][0]["message"]
