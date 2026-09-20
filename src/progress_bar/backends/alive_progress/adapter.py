"""Progress reporting backed by :mod:`alive_progress`."""

from __future__ import annotations

from contextlib import AbstractContextManager, ExitStack
from typing import cast

from alive_progress import alive_bar

from progress_bar.backend import ProgressBarBackend
from progress_bar.backends.alive_progress.bar_handle import AliveBarHandle
from progress_bar.environment import RenderEnvironment
from progress_bar.reporter import ProgressReporter
from progress_bar.settings import ProgressSettings


class AliveProgressAdapter(ProgressReporter):
    """Reporter rendering with the ``alive-progress`` package.

    The underlying bar is a context manager, so its scope is kept open by
    an :class:`~contextlib.ExitStack` for the lifetime of the reporter.

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
        super().__init__(settings, environment)
        self._stack = ExitStack()
        self._handle: AliveBarHandle | None = None

    @property
    def backend(self) -> ProgressBarBackend:
        """Backend this reporter renders with."""
        return ProgressBarBackend.ALIVE_PROGRESS

    def _open(self) -> None:
        bar_context = cast(
            AbstractContextManager[AliveBarHandle],
            alive_bar(
                self._settings.total,
                title=self._settings.description or None,
                file=self._environment.stream,
                receipt=self._settings.is_leave_visible,
            ),
        )
        self._handle = self._stack.enter_context(bar_context)

    def _render(self, step: int) -> None:
        if self._handle is None:
            raise RuntimeError("alive_progress bar is not initialized")
        self._handle(step)

    def _close(self) -> None:
        self._handle = None
        self._stack.close()
