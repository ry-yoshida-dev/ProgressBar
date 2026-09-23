"""Dependency-free progress bar rendered on a plain text stream."""

from __future__ import annotations

from progress_bar.backend import ProgressBarBackend
from progress_bar.backends.plain.formatter import PlainBarFormatter
from progress_bar.environment import RenderEnvironment
from progress_bar.renderer import ProgressRenderer
from progress_bar.settings import ProgressSettings


class PlainRenderer(ProgressRenderer):
    """Renderer writing a textual bar without any third-party package.

    On an interactive terminal the line is redrawn in place. On a
    redirected stream a new line is emitted only when a milestone is
    reached, which keeps log files readable, and the final line is
    written once rather than repeating the last milestone.

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
        self._formatter = PlainBarFormatter()
        self._last_logged_milestone = 0
        self._last_written_line = ""

    def _open(self) -> None:
        self._last_logged_milestone = 0
        self._last_written_line = ""
        if self._environment.is_terminal:
            self._write_line(self._format_line(), "\r")

    def _render(self, step: int) -> None:
        if self._environment.is_terminal:
            self._write_line(self._format_line(), "\r")
            return
        milestone = self._formatter.milestone(self._settings, self._completed)
        if milestone > self._last_logged_milestone:
            self._last_logged_milestone = milestone
            self._write_line(self._format_line(), "\n")

    def _close(self) -> None:
        if not self._settings.is_leave_visible:
            if self._environment.is_terminal:
                self._write(f"\r{' ' * len(self._format_line())}\r")
            return
        line = self._format_line()
        if not self._environment.is_terminal and line == self._last_written_line:
            return
        self._write_line(line, "\n")

    def _write_line(self, line: str, terminator: str) -> None:
        self._last_written_line = line
        self._write(f"{line}{terminator}")

    def _write(self, text: str) -> None:
        self._environment.stream.write(text)
        self._environment.stream.flush()

    def _format_line(self) -> str:
        return self._formatter.format_line(self._settings, self._completed)

    @property
    def backend(self) -> ProgressBarBackend:
        """Backend implemented by this renderer."""
        return ProgressBarBackend.PLAIN
