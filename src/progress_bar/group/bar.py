"""Handle of one bar displayed by a progress bar group."""

from __future__ import annotations

from typing import TYPE_CHECKING

from progress_bar.group.task import ProgressTask
from progress_bar.settings import ProgressSettings

if TYPE_CHECKING:
    from progress_bar.group.group import ProgressBarGroup


class GroupedProgressBar(ProgressTask):
    """Bar of a :class:`~progress_bar.ProgressBarGroup`, rendered by the group.

    Instances are created by :meth:`ProgressBarGroup.add`, which has
    already displayed the bar. Every call is forwarded to the group, which
    serializes them, so the bars of one group can be advanced from
    different threads.

    Parameters
    ----------
    group
        Group displaying the bar.
    key
        Identifier of the bar within the group.
    settings
        Rendering settings of the bar.
    """

    def __init__(
        self, group: ProgressBarGroup, key: str, settings: ProgressSettings
    ) -> None:
        self._group = group
        self._key = key
        self._settings = settings
        self._completed = 0
        self._is_active = True

    def advance(self, step: int = 1) -> None:
        """Record completed steps.

        Parameters
        ----------
        step
            Number of steps completed since the previous call. Zero is
            accepted and leaves the bar untouched.

        Raises
        ------
        ValueError
            If ``step`` is negative.
        RuntimeError
            If the bar is already finished.
        """
        if step < 0:
            raise ValueError(f"step must not be negative, got {step}")
        if not self._is_active:
            raise RuntimeError("the bar is already finished")
        self._completed += step
        self._group.advance_bar(self._key, step)

    def finish(self) -> None:
        """Finalize the bar, ignoring a bar that is already finished."""
        if not self._is_active:
            return
        self._is_active = False
        self._group.finish_bar(self._key)

    @property
    def completed(self) -> int:
        """Number of steps recorded so far."""
        return self._completed

    @property
    def settings(self) -> ProgressSettings:
        """Rendering settings of the bar."""
        return self._settings

    @property
    def is_active(self) -> bool:
        """Whether the bar is still running."""
        return self._is_active
