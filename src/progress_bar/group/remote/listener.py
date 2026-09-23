"""Thread applying the events of worker processes to a progress bar group."""

from __future__ import annotations

import threading
from multiprocessing.queues import Queue
from typing import TYPE_CHECKING, Final

from progress_bar.group.remote.bar_advanced import RemoteBarAdvanced
from progress_bar.group.remote.bar_finished import RemoteBarFinished
from progress_bar.group.remote.bar_opened import RemoteBarOpened
from progress_bar.group.remote.event import RemoteBarEvent

if TYPE_CHECKING:
    from progress_bar.group.group import ProgressBarGroup


class RemoteEventListener:
    """Drains the queue of remote events on a daemon thread of the parent.

    Events are applied in the order they arrive. An event about a bar the
    group no longer displays is ignored, so a worker that outlives the
    group, or reports after it was stopped, cannot break it.

    Parameters
    ----------
    queue
        Queue the worker processes send their events to.
    group
        Group rendering the remote bars.
    """

    STOP_TIMEOUT_SECONDS: Final[float] = 5.0

    def __init__(
        self, queue: Queue[RemoteBarEvent | None], group: ProgressBarGroup
    ) -> None:
        self._queue = queue
        self._group = group
        self._thread = threading.Thread(
            target=self._run, name="progress-bar-remote-listener", daemon=True
        )

    def start(self) -> None:
        """Start draining the queue."""
        self._thread.start()

    def stop(self) -> None:
        """Apply the events already queued, then stop the thread."""
        self._queue.put(None)
        self._thread.join(timeout=self.STOP_TIMEOUT_SECONDS)
        self._queue.close()

    def _run(self) -> None:
        while True:
            event = self._queue.get()
            if event is None:
                return
            self._apply(event)

    def _apply(self, event: RemoteBarEvent) -> None:
        match event:
            case RemoteBarOpened(key=key, settings=settings):
                self._group.open_bar(key, settings)
            case RemoteBarAdvanced(key=key, step=step):
                self._group.advance_bar(key, step)
            case RemoteBarFinished(key=key):
                self._group.finish_bar(key)

    @property
    def queue(self) -> Queue[RemoteBarEvent | None]:
        """Queue the worker processes send their events to."""
        return self._queue
