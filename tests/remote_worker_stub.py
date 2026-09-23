"""Work run in a worker process that reports to a remote progress bar group."""

from __future__ import annotations

from typing import ClassVar

from progress_bar import RemoteProgressBarGroup


class RemoteWorkerStub:
    """Process pool task advancing a bar of the group its pool was given.

    :meth:`initialize` is the pool initializer, since the queue behind a
    :class:`RemoteProgressBarGroup` can only reach a worker through
    inheritance, and :meth:`run` is the submitted task.
    """

    _group: ClassVar[RemoteProgressBarGroup | None] = None

    @staticmethod
    def initialize(group: RemoteProgressBarGroup) -> None:
        """Keep the group for the tasks this worker runs.

        Parameters
        ----------
        group
            Proxy of the group living in the parent process.
        """
        RemoteWorkerStub._group = group

    @staticmethod
    def run(description: str, step_count: int, is_leave_visible: bool) -> int:
        """Advance one bar of the group ``step_count`` times.

        Parameters
        ----------
        description
            Label of the bar.
        step_count
            Number of steps to report.
        is_leave_visible
            Whether the finished bar stays on screen.

        Returns
        -------
        int
            Number of steps the bar recorded.

        Raises
        ------
        RuntimeError
            If the worker was not initialized with a group.
        """
        group = RemoteWorkerStub._group
        if group is None:
            raise RuntimeError("the worker was not initialized with a group")
        task = group.add(
            total=step_count,
            description=description,
            is_leave_visible=is_leave_visible,
        )
        for _ in task.report(range(step_count)):
            pass
        return task.completed
