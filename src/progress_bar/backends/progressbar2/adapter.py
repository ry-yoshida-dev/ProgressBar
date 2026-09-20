"""Progress reporting backed by :mod:`progressbar` (the progressbar2 package)."""

from __future__ import annotations

import progressbar

from progress_bar.backend import ProgressBarBackend
from progress_bar.environment import RenderEnvironment
from progress_bar.reporter import ProgressReporter
from progress_bar.settings import ProgressSettings


class ProgressBar2Adapter(ProgressReporter):
    """Reporter rendering with the ``progressbar2`` package.

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
        self._bar: progressbar.ProgressBar | None = None

    @property
    def backend(self) -> ProgressBarBackend:
        """Backend this reporter renders with."""
        return ProgressBarBackend.PROGRESSBAR2

    def _open(self) -> None:
        total = self._settings.total
        max_value = progressbar.UnknownLength if total is None else total
        description = self._settings.description
        self._bar = progressbar.ProgressBar(
            max_value=max_value,
            prefix=f"{description} " if description else "",
            fd=self._environment.stream,
        )
        self._bar.start()

    def _render(self, step: int) -> None:
        if self._bar is None:
            raise RuntimeError("progressbar2 bar is not initialized")
        self._bar.update(self._completed)

    def _close(self) -> None:
        if self._bar is None:
            return
        self._bar.finish(end="\n" if self._settings.is_leave_visible else "\r")
        self._bar = None
