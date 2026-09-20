"""Rendering settings shared by every progress bar backend."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProgressSettings:
    """Backend-independent description of a task to be displayed.

    Parameters
    ----------
    total
        Number of steps the task consists of, or ``None`` when the length
        is unknown and only a running counter can be displayed. Zero is a
        valid total describing an empty task.
    description
        Label rendered next to the bar.
    unit
        Name of a single step, used by the backends that display a rate.
    is_leave_visible
        Whether the finished bar stays on screen after completion.

    Raises
    ------
    ValueError
        If ``total`` is negative or ``unit`` is empty.
    """

    total: int | None = None
    description: str = ""
    unit: str = "it"
    is_leave_visible: bool = True

    def __post_init__(self) -> None:
        if self.total is not None and self.total < 0:
            raise ValueError(f"total must not be negative, got {self.total}")
        if not self.unit:
            raise ValueError("unit must be a non-empty string")
