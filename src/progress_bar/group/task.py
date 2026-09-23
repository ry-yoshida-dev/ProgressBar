"""Interface of one bar handed out by a progress bar source."""

from __future__ import annotations

from collections.abc import Generator, Iterable
from types import TracebackType
from typing import Protocol, Self


class ProgressTask(Protocol):
    """One running bar, already displayed when it is handed out.

    Implementations provide :meth:`advance`, :meth:`finish` and
    :attr:`completed`; iterating with :meth:`report` and using the task as
    a context manager are built on top of them.
    """

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
            If the task is already finished.
        """
        ...

    def finish(self) -> None:
        """Finalize the bar, ignoring a task that is already finished."""
        ...

    @property
    def completed(self) -> int:
        """Number of steps recorded so far."""
        ...

    def report[ItemT](self, iterable: Iterable[ItemT]) -> Generator[ItemT, None, None]:
        """Yield the items of ``iterable`` while advancing the bar.

        The task is finished once ``iterable`` is exhausted or the returned
        generator is closed, so wrap the generator in
        ``contextlib.closing`` when a loop may stop early while a
        reference to it survives.

        Parameters
        ----------
        iterable
            Items to iterate over.

        Yields
        ------
        ItemT
            The items of ``iterable``, unchanged.
        """
        try:
            for item in iterable:
                yield item
                self.advance()
        finally:
            self.finish()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.finish()
