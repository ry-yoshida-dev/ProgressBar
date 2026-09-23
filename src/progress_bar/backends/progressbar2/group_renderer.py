"""Group of progress bars rendered with :mod:`progressbar` (progressbar2)."""

from __future__ import annotations

from typing import Final, TextIO, cast

import progressbar

from progress_bar.backend import ProgressBarBackend
from progress_bar.environment import RenderEnvironment
from progress_bar.group.renderer import ProgressGroupRenderer
from progress_bar.settings import ProgressSettings


class ProgressBar2GroupRenderer(ProgressGroupRenderer):
    """Group renderer drawing every bar through one ``progressbar.MultiBar``.

    ``MultiBar`` redraws its bars from a background thread, from top to
    bottom in the order they were added. A finished bar that stays visible
    keeps its line, and any other bar is removed from the display.

    Parameters
    ----------
    environment
        Output stream and terminal capabilities to render with.
    """

    CLOSE_TIMEOUT_SECONDS: Final[float] = 5.0

    def __init__(self, environment: RenderEnvironment) -> None:
        super().__init__(environment)
        self._multibar: progressbar.MultiBar | None = None

    def _open(self) -> None:
        multibar = progressbar.MultiBar(
            fd=cast(TextIO, self._environment.stream),
            prepend_label=False,
            initial_format=None,
        )
        multibar.start()
        self._multibar = multibar

    def _add_bar(self, key: str, settings: ProgressSettings) -> None:
        total = settings.total
        description = settings.description
        bar = progressbar.ProgressBar(
            max_value=progressbar.UnknownLength if total is None else total,
            prefix=f"{description} " if description else "",
        )
        multibar = self._require_multibar()
        multibar[key] = bar
        bar.start()

    def _render_bar(self, key: str, step: int) -> None:
        self._require_multibar()[key].update(self._completed_by_key[key])

    def _finish_bar(self, key: str) -> None:
        multibar = self._require_multibar()
        multibar[key].finish()
        if not self._settings_by_key[key].is_leave_visible:
            del multibar[key]

    def _close(self) -> None:
        if self._multibar is None:
            return
        self._multibar.join(timeout=self.CLOSE_TIMEOUT_SECONDS)
        self._multibar.stop(timeout=self.CLOSE_TIMEOUT_SECONDS)
        self._multibar = None

    def _require_multibar(self) -> progressbar.MultiBar:
        if self._multibar is None:
            raise RuntimeError("progressbar2 multibar is not initialized")
        return self._multibar

    @property
    def backend(self) -> ProgressBarBackend:
        """Backend implemented by this renderer."""
        return ProgressBarBackend.PROGRESSBAR2
