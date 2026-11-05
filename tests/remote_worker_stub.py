"""Work run in a worker process that reports to a remote progress bar group."""

from __future__ import annotations

from typing import ClassVar

from progress_bar import RemoteProgressBarGroup


class RemoteWorkerStub:
    """Process pool task advancing a bar of the group its pool was given.

    :meth:`initialize` is the pool initializer, since the queue behind a
    :class:`RemoteProgressBarGroup` can only reach a worker through
    inheritance, and :meth:`run` and :meth:`run_without_finishing` are the
    submitted tasks.
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
        task = RemoteWorkerStub._require_group().add(
            total=step_count,
            description=description,
            is_leave_visible=is_leave_visible,
        )
        for _ in task.report(range(step_count)):
            pass
        return task.completed

    @staticmethod
    def run_without_finishing(description: str, step_count: int) -> int:
        """Report ``step_count`` steps of one bar of the group and leave it open.

        Parameters
        ----------
        description
            Label of the bar.
        step_count
            Number of steps to report, also the total of the bar so that the
            last step is sent at once.

        Returns
        -------
        int
            Number of steps the bar recorded.

        Raises
        ------
        RuntimeError
            If the worker was not initialized with a group.
        """
        task = RemoteWorkerStub._require_group().add(
            total=step_count, description=description
        )
        task.advance(step_count)
        return task.completed

    @staticmethod
    def _require_group() -> RemoteProgressBarGroup:
        group = RemoteWorkerStub._group
        if group is None:
            raise RuntimeError("the worker was not initialized with a group")
        return group
