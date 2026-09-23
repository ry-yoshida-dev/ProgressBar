"""Bar of a worker process, rendered by the group of the parent process."""

from __future__ import annotations

import time
import uuid
from multiprocessing.queues import Queue
from typing import Final

from progress_bar.group.remote.bar_advanced import RemoteBarAdvanced
from progress_bar.group.remote.bar_finished import RemoteBarFinished
from progress_bar.group.remote.bar_opened import RemoteBarOpened
from progress_bar.group.remote.event import RemoteBarEvent
from progress_bar.group.task import ProgressTask
from progress_bar.settings import ProgressSettings


class RemoteProgressBar(ProgressTask):
    """Bar that sends its progress to a group living in another process.

    Instances are created by :meth:`RemoteProgressBarGroup.add`. Steps are
    accumulated locally and sent at most once per
    :attr:`FLUSH_INTERVAL_SECONDS`, and whenever the known total is
    reached, so a tight loop does not flood the queue with one event per
    step.

    Parameters
    ----------
    queue
        Queue drained by the group, or ``None`` when the group does not
        display anything, in which case no event is sent.
    settings
        Rendering settings of the bar.
    """

    FLUSH_INTERVAL_SECONDS: Final[float] = 0.1

    def __init__(
        self,
        queue: Queue[RemoteBarEvent | None] | None,
        settings: ProgressSettings,
    ) -> None:
        self._queue = queue
        self._settings = settings
        self._key = uuid.uuid4().hex
        self._completed = 0
        self._pending_step = 0
        self._last_flush_time = time.monotonic()
        self._is_active = True
        self._send(RemoteBarOpened(self._key, settings))

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
        self._pending_step += step
        if self._is_flush_due():
            self._flush()

    def finish(self) -> None:
        """Send the remaining steps and finalize the bar.

        A bar that is already finished is ignored.
        """
        if not self._is_active:
            return
        self._is_active = False
        self._flush()
        self._send(RemoteBarFinished(self._key))

    def _is_flush_due(self) -> bool:
        total = self._settings.total
        if total is not None and self._completed >= total:
            return True
        elapsed = time.monotonic() - self._last_flush_time
        return elapsed >= self.FLUSH_INTERVAL_SECONDS

    def _flush(self) -> None:
        if self._pending_step > 0:
            self._send(RemoteBarAdvanced(self._key, self._pending_step))
            self._pending_step = 0
        self._last_flush_time = time.monotonic()

    def _send(self, event: RemoteBarEvent) -> None:
        if self._queue is not None:
            self._queue.put(event)

    @property
    def completed(self) -> int:
        """Number of steps recorded so far, including unsent ones."""
        return self._completed

    @property
    def settings(self) -> ProgressSettings:
        """Rendering settings of the bar."""
        return self._settings

    @property
    def is_active(self) -> bool:
        """Whether the bar is still running."""
        return self._is_active
