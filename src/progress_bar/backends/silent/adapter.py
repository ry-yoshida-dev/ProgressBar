"""Progress reporting that renders nothing."""

from __future__ import annotations

from progress_bar.backend import ProgressBarBackend
from progress_bar.reporter import ProgressReporter


class SilentAdapter(ProgressReporter):
    """Reporter that tracks progress without producing any output.

    It is selected when progress display is disabled, which keeps calling
    code free of conditional branches.
    """

    @property
    def backend(self) -> ProgressBarBackend:
        """Backend this reporter renders with."""
        return ProgressBarBackend.SILENT

    def _open(self) -> None:
        return

    def _render(self, step: int) -> None:
        return

    def _close(self) -> None:
        return
