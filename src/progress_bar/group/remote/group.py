"""Worker-side proxy of a progress bar group living in another process."""

from __future__ import annotations

from multiprocessing.queues import Queue

from progress_bar.group.remote.bar import RemoteProgressBar
from progress_bar.group.remote.event import RemoteBarEvent
from progress_bar.group.source import ProgressBarSource
from progress_bar.settings import ProgressSettings


class RemoteProgressBarGroup(ProgressBarSource):
    """Displays bars of a worker process in the group that created it.

    Obtained from :meth:`ProgressBarGroup.remote` in the parent process
    and handed to worker processes. Every bar it adds is rendered by that
    group, next to the bars of the parent and of the other workers.

    The underlying :class:`multiprocessing.Queue` can only reach a child
    process through inheritance, so pass this object when the process is
    created, for instance through the ``initializer`` and ``initargs`` of
    :class:`concurrent.futures.ProcessPoolExecutor`, rather than as an
    argument of a submitted task.

    Parameters
    ----------
    queue
        Queue drained by the group, or ``None`` when the group does not
        display anything, which turns every bar into a silent counter.
    """

    def __init__(self, queue: Queue[RemoteBarEvent | None] | None) -> None:
        self._queue = queue

    def add(
        self,
        total: int | None = None,
        description: str = "",
        *,
        unit: str = "it",
        is_leave_visible: bool = True,
    ) -> RemoteProgressBar:
        """Display a new bar in the parent's group.

        Parameters
        ----------
        total
            Number of steps of the task, or ``None`` when unknown.
        description
            Label rendered next to the bar.
        unit
            Name of a single step.
        is_leave_visible
            Whether the finished bar stays on screen.

        Returns
        -------
        RemoteProgressBar
            The running bar.

        Raises
        ------
        ValueError
            If ``total`` is negative or ``unit`` is empty.
        """
        settings = ProgressSettings(
            total=total,
            description=description,
            unit=unit,
            is_leave_visible=is_leave_visible,
        )
        return RemoteProgressBar(self._queue, settings)

    def remote(self) -> RemoteProgressBarGroup:
        """Return this proxy, for handing over to processes this worker creates.

        The underlying queue is inherited by a grandchild process just as by
        a child, so the bars of nested pools reach the same group.

        Returns
        -------
        RemoteProgressBarGroup
            This proxy.
        """
        return self

    @property
    def is_enabled(self) -> bool:
        """Whether the bars reach a group that displays them."""
        return self._queue is not None
