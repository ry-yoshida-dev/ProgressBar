"""Backend-independent progress reporting interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType

from progress_bar.backend import ProgressBarBackend
from progress_bar.environment import RenderEnvironment
from progress_bar.settings import ProgressSettings


class ProgressReporter(ABC):
    """Lifecycle of a single progress bar, independent of its backend.

    Concrete subclasses adapt one third-party library by implementing
    :meth:`_open`, :meth:`_render` and :meth:`_close`.

    Parameters
    ----------
    settings
        Rendering settings of the task to display.
    environment
        Output stream and terminal capabilities to render with.
    """

    def __init__(
        self, settings: ProgressSettings, environment: RenderEnvironment
    ) -> None:
        self._settings = settings
        self._environment = environment
        self._completed = 0
        self._is_active = False

    @property
    @abstractmethod
    def backend(self) -> ProgressBarBackend:
        """Backend this reporter renders with."""

    @property
    def settings(self) -> ProgressSettings:
        """Rendering settings of the displayed task."""
        return self._settings

    @property
    def environment(self) -> RenderEnvironment:
        """Environment the bar is rendered in."""
        return self._environment

    @property
    def completed(self) -> int:
        """Number of steps reported so far."""
        return self._completed

    @property
    def is_active(self) -> bool:
        """Whether the bar is currently displayed."""
        return self._is_active

    def start(self) -> None:
        """Display the bar.

        Raises
        ------
        RuntimeError
            If the bar is already displayed.
        """
        if self._is_active:
            raise RuntimeError(f"{type(self).__name__} is already started")
        self._open()
        self._is_active = True

    def advance(self, step: int = 1) -> None:
        """Report completed steps.

        Parameters
        ----------
        step
            Number of steps completed since the previous call. Zero is
            accepted and leaves the bar untouched, so callers can report
            the size of a batch without special casing an empty one.

        Raises
        ------
        ValueError
            If ``step`` is negative.
        RuntimeError
            If the bar has not been started.
        """
        if step < 0:
            raise ValueError(f"step must not be negative, got {step}")
        if not self._is_active:
            raise RuntimeError(f"{type(self).__name__} is not started")
        if step == 0:
            return
        self._completed += step
        self._render(step)

    def finish(self) -> None:
        """Remove or finalize the bar, ignoring a bar that never started."""
        if not self._is_active:
            return
        self._is_active = False
        self._close()

    def __enter__(self) -> ProgressReporter:
        self.start()
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.finish()

    @abstractmethod
    def _open(self) -> None:
        """Create and display the underlying bar."""

    @abstractmethod
    def _render(self, step: int) -> None:
        """Advance the underlying bar by ``step`` steps."""

    @abstractmethod
    def _close(self) -> None:
        """Release the resources held by the underlying bar."""
