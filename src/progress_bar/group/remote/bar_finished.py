"""Event announcing that a bar of a worker process finished."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RemoteBarFinished:
    """A worker process finished one of its bars.

    Parameters
    ----------
    key
        Identifier of the bar.
    """

    key: str
