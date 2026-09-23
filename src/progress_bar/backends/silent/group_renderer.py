"""Group of progress bars that renders nothing."""

from __future__ import annotations

from progress_bar.backend import ProgressBarBackend
from progress_bar.group.renderer import ProgressGroupRenderer
from progress_bar.settings import ProgressSettings


class SilentGroupRenderer(ProgressGroupRenderer):
    """Group renderer that counts steps without producing any output.

    It is selected when progress display is disabled, which keeps calling
    code free of conditional branches.
    """

    def _open(self) -> None:
        return

    def _add_bar(self, key: str, settings: ProgressSettings) -> None:
        return

    def _render_bar(self, key: str, step: int) -> None:
        return

    def _finish_bar(self, key: str) -> None:
        return

    def _close(self) -> None:
        return

    @property
    def backend(self) -> ProgressBarBackend:
        """Backend implemented by this renderer."""
        return ProgressBarBackend.SILENT
