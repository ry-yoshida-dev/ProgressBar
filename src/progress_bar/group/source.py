"""Interface of an object that displays new bars on request."""

from __future__ import annotations

from collections.abc import Generator, Iterable, Sized
from typing import TYPE_CHECKING, Protocol

from progress_bar.group.task import ProgressTask

if TYPE_CHECKING:
    from progress_bar.group.remote.group import RemoteProgressBarGroup


class ProgressBarSource(Protocol):
    """Displays bars that run side by side with the other bars it displays.

    :class:`~progress_bar.ProgressBarGroup` renders them in the current
    process, and :class:`~progress_bar.RemoteProgressBarGroup` forwards
    them from a worker process to the group that created it, so code
    typed against this protocol runs unchanged in either place.
    Implementations provide :meth:`add` and :meth:`remote`; :meth:`report` is
    built on :meth:`add`.
    """

    def add(
        self,
        total: int | None = None,
        description: str = "",
        *,
        unit: str = "it",
        is_leave_visible: bool = True,
    ) -> ProgressTask:
        """Display a new bar.

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
        ProgressTask
            The running bar.

        Raises
        ------
        ValueError
            If ``total`` is negative or ``unit`` is empty.
        """
        ...

    def remote(self) -> RemoteProgressBarGroup:
        """Return a proxy through which worker processes add bars here.

        Pass the proxy to a worker when the process is created, since the
        queue behind it only reaches a child through inheritance.

        Returns
        -------
        RemoteProgressBarGroup
            Proxy to hand to worker processes.
        """
        ...

    def report[ItemT](
        self,
        iterable: Iterable[ItemT],
        total: int | None = None,
        description: str = "",
        *,
        unit: str = "it",
        is_leave_visible: bool = True,
    ) -> Generator[ItemT, None, None]:
        """Yield the items of ``iterable`` while a new bar advances.

        The bar is displayed by this call, before iteration starts, so it
        keeps its place above bars added later, and finished once
        ``iterable`` is exhausted or the returned generator is closed.

        Parameters
        ----------
        iterable
            Items to iterate over.
        total
            Number of steps of the task. Defaults to the length of
            ``iterable`` when it has one, and to an unknown total otherwise.
        description
            Label rendered next to the bar.
        unit
            Name of a single step.
        is_leave_visible
            Whether the finished bar stays on screen.

        Returns
        -------
        Generator[ItemT, None, None]
            The items of ``iterable``, unchanged.
        """
        if total is None and isinstance(iterable, Sized):
            total = len(iterable)
        task = self.add(
            total,
            description,
            unit=unit,
            is_leave_visible=is_leave_visible,
        )
        return task.report(iterable)
