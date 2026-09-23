"""Event reporting steps completed by a bar of a worker process."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RemoteBarAdvanced:
    """A worker process completed steps of one of its bars.

    Parameters
    ----------
    key
        Identifier of the bar.
    step
        Number of steps completed since the previous event of the bar.
    """

    key: str
    step: int
