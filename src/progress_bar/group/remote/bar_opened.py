"""Event announcing a bar opened in a worker process."""

from __future__ import annotations

from dataclasses import dataclass

from progress_bar.settings import ProgressSettings


@dataclass(frozen=True, slots=True)
class RemoteBarOpened:
    """A worker process displayed a new bar.

    Parameters
    ----------
    key
        Identifier of the bar, unique across every process.
    settings
        Rendering settings of the bar.
    """

    key: str
    settings: ProgressSettings
