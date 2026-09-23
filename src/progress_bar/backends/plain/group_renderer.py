"""Dependency-free group of progress bars rendered on a plain text stream."""

from __future__ import annotations

import time
from typing import Final

from progress_bar.backend import ProgressBarBackend
from progress_bar.backends.plain.formatter import PlainBarFormatter
from progress_bar.environment import RenderEnvironment
from progress_bar.group.renderer import ProgressGroupRenderer
from progress_bar.settings import ProgressSettings


class PlainGroupRenderer(ProgressGroupRenderer):
    """Group renderer writing textual bars without any third-party package.

    On an interactive terminal the open bars form a block of lines that is
    redrawn in place with ANSI cursor movement, at most once per
    :attr:`REDRAW_INTERVAL_SECONDS` while steps are reported. A finished bar
    that stays visible is written once above the block, so the block only
    ever holds bars that are still running.

    On a redirected stream every bar writes a line of its own at each
    milestone, labelled with its description, and a bar that stays visible
    writes its final state once when it finishes.

    Parameters
    ----------
    environment
        Output stream and terminal capabilities to render with.
    """

    REDRAW_INTERVAL_SECONDS: Final[float] = 0.1

    def __init__(self, environment: RenderEnvironment) -> None:
        super().__init__(environment)
        self._formatter = PlainBarFormatter()
        self._drawn_line_count = 0
        self._last_redraw_time = 0.0
        self._pending_permanent_lines: list[str] = []
        self._last_logged_milestone_by_key: dict[str, int] = {}
        self._last_written_line_by_key: dict[str, str] = {}

    def _open(self) -> None:
        self._drawn_line_count = 0
        self._last_redraw_time = 0.0
        self._pending_permanent_lines = []

    def _add_bar(self, key: str, settings: ProgressSettings) -> None:
        if self._environment.is_terminal:
            self._redraw()
            return
        self._last_logged_milestone_by_key[key] = 0
        self._last_written_line_by_key[key] = ""

    def _render_bar(self, key: str, step: int) -> None:
        if self._environment.is_terminal:
            if self._is_redraw_due(key):
                self._redraw()
            return
        settings = self._settings_by_key[key]
        milestone = self._formatter.milestone(settings, self._completed_by_key[key])
        if milestone > self._last_logged_milestone_by_key[key]:
            self._last_logged_milestone_by_key[key] = milestone
            self._log_line(key)

    def _finish_bar(self, key: str) -> None:
        settings = self._settings_by_key[key]
        if self._environment.is_terminal:
            if settings.is_leave_visible:
                self._pending_permanent_lines.append(self._format_line(key))
            self._redraw(finishing_key=key)
            return
        if settings.is_leave_visible:
            line = self._format_line(key)
            if line != self._last_written_line_by_key[key]:
                self._write(f"{line}\n")
        del self._last_logged_milestone_by_key[key]
        del self._last_written_line_by_key[key]

    def _close(self) -> None:
        if self._environment.is_terminal:
            self._redraw()

    def _is_redraw_due(self, key: str) -> bool:
        total = self._settings_by_key[key].total
        if total is not None and self._completed_by_key[key] >= total:
            return True
        elapsed = time.monotonic() - self._last_redraw_time
        return elapsed >= self.REDRAW_INTERVAL_SECONDS

    def _redraw(self, finishing_key: str | None = None) -> None:
        live_lines = [
            self._format_line(key)
            for key in self._settings_by_key
            if key != finishing_key
        ]
        written_lines = self._pending_permanent_lines + live_lines
        cleared_line_count = max(self._drawn_line_count - len(written_lines), 0)
        parts: list[str] = []
        if self._drawn_line_count > 0:
            parts.append(f"\x1b[{self._drawn_line_count}F")
        parts.extend(f"\x1b[2K{line}\n" for line in written_lines)
        if cleared_line_count > 0:
            parts.append("\x1b[2K\n" * cleared_line_count)
            parts.append(f"\x1b[{cleared_line_count}F")
        self._write("".join(parts))
        self._pending_permanent_lines = []
        self._drawn_line_count = len(live_lines)
        self._last_redraw_time = time.monotonic()

    def _log_line(self, key: str) -> None:
        line = self._format_line(key)
        self._last_written_line_by_key[key] = line
        self._write(f"{line}\n")

    def _format_line(self, key: str) -> str:
        return self._formatter.format_line(
            self._settings_by_key[key], self._completed_by_key[key]
        )

    def _write(self, text: str) -> None:
        if text == "":
            return
        self._environment.stream.write(text)
        self._environment.stream.flush()

    @property
    def backend(self) -> ProgressBarBackend:
        """Backend implemented by this renderer."""
        return ProgressBarBackend.PLAIN
