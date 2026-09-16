from __future__ import annotations

from dataclasses import dataclass


VALID_STATUSES = {"pending", "in_progress", "done", "blocked"}


@dataclass
class PlanStep:
    text: str
    status: str = "pending"
    evidence: str = ""


class Plan:
    """Small mutable execution plan kept outside raw chat history."""

    def __init__(self):
        self.steps: list[PlanStep] = []
        self.revision = 0
        self.last_revision_reason = ""

    def set_steps(self, steps: list[str], reason: str = "") -> str:
        cleaned = [str(step).strip() for step in steps if str(step).strip()]
        if not 2 <= len(cleaned) <= 6:
            raise ValueError("plan must contain between 2 and 6 non-empty steps")
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("plan steps must be unique")

        if self.steps:
            self.revision += 1
            self.last_revision_reason = reason.strip() or "revised from new evidence"

        self.steps = [PlanStep(text=step) for step in cleaned]
        return self.render()

    def update_step(self, index: int, status: str, evidence: str = "") -> str:
        if not self.steps:
            raise ValueError("create a plan first")
        if status not in VALID_STATUSES:
            raise ValueError(f"invalid status: {status}")
        if not 0 <= index < len(self.steps):
            raise IndexError(f"step index out of range: {index}")
        if status == "done" and not evidence.strip():
            raise ValueError("done steps require evidence")

        step = self.steps[index]
        step.status = status
        step.evidence = evidence.strip()
        return self.render()

    def render(self) -> str:
        if not self.steps:
            return "(no plan)"
        lines = [f"Plan r{self.revision}"]
        if self.last_revision_reason:
            lines.append(f"revision reason: {self.last_revision_reason}")
        for index, step in enumerate(self.steps):
            suffix = f" — evidence: {step.evidence}" if step.evidence else ""
            lines.append(f"{index}. [{step.status}] {step.text}{suffix}")
        return "\n".join(lines)
