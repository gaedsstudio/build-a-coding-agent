from __future__ import annotations

from dataclasses import dataclass
import json
import math
from typing import Any


Message = dict[str, Any]


class ContextBudgetError(ValueError):
    """Raised when mandatory context alone cannot fit in the configured budget."""


def estimate_tokens(value: Any) -> int:
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return max(1, math.ceil(len(text) / 4))


@dataclass(frozen=True)
class ContextReport:
    budget_tokens: int
    estimated_tokens: int
    kept_turns: int
    dropped_turns: int

    def line(self) -> str:
        return (
            f"context≈{self.estimated_tokens}/{self.budget_tokens} tokens "
            f"| kept_turns={self.kept_turns} | dropped_turns={self.dropped_turns}"
        )


class ContextWindow:
    def __init__(self, system_prompt: str, user_task: str, max_tokens: int = 12_000):
        if max_tokens < 128:
            raise ValueError("max_tokens must be at least 128")
        self.max_tokens = int(max_tokens)
        self._pinned: list[Message] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_task},
        ]
        self._turns: list[list[Message]] = []
        self._last_report = ContextReport(self.max_tokens, estimate_tokens(self._pinned), 0, 0)

    def add_turn(self, assistant_message: Message, tool_messages: list[Message]) -> None:
        if assistant_message.get("role") != "assistant":
            raise ValueError("turn must start with an assistant message")
        for message in tool_messages:
            if message.get("role") != "tool":
                raise ValueError("tool_messages may only contain role='tool'")
        self._turns.append([assistant_message, *tool_messages])

    @staticmethod
    def _messages_tokens(messages: list[Message]) -> int:
        return sum(estimate_tokens(message) for message in messages)

    def messages(self, extra_pinned: list[Message] | None = None) -> list[Message]:
        pinned = [*self._pinned, *(extra_pinned or [])]
        base_tokens = self._messages_tokens(pinned)
        if base_tokens > self.max_tokens:
            self._last_report = ContextReport(
                budget_tokens=self.max_tokens,
                estimated_tokens=base_tokens,
                kept_turns=0,
                dropped_turns=len(self._turns),
            )
            raise ContextBudgetError(
                f"pinned context needs about {base_tokens} tokens but the budget is {self.max_tokens}; "
                "increase AGENT_CONTEXT_TOKENS or shorten the task/plan"
            )

        remaining = self.max_tokens - base_tokens
        selected_reversed: list[list[Message]] = []
        selected_tokens = 0

        for turn in reversed(self._turns):
            turn_tokens = self._messages_tokens(turn)
            if turn_tokens <= remaining - selected_tokens:
                selected_reversed.append(turn)
                selected_tokens += turn_tokens
                continue
            break

        selected = list(reversed(selected_reversed))
        flattened = [message for turn in selected for message in turn]
        self._last_report = ContextReport(
            budget_tokens=self.max_tokens,
            estimated_tokens=base_tokens + selected_tokens,
            kept_turns=len(selected),
            dropped_turns=len(self._turns) - len(selected),
        )
        return [*pinned, *flattened]

    def report(self) -> ContextReport:
        return self._last_report
