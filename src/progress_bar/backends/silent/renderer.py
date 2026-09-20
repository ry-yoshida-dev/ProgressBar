"""Progress bar that renders nothing."""

from __future__ import annotations

from progress_bar.backend import ProgressBarBackend
from progress_bar.renderer import ProgressRenderer


class SilentRenderer(ProgressRenderer):
    """Renderer that counts steps without producing any output.

    It is selected when progress display is disabled, which keeps calling
    code free of conditional branches.
    """

    def _open(self) -> None:
        return

    def _render(self, step: int) -> None:
        return

    def _close(self) -> None:
        return

    @property
    def backend(self) -> ProgressBarBackend:
        """Backend implemented by this renderer."""
        return ProgressBarBackend.SILENT
