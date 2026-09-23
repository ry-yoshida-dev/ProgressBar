"""Text formatting shared by the dependency-free renderers."""

from __future__ import annotations

from typing import Final

from progress_bar.settings import ProgressSettings


class PlainBarFormatter:
    """Formats one bar as a line of text and tracks its logging milestones.

    A milestone is reached every ten percent of a known total, or every
    hundred steps of an unknown one. Renderers writing to a redirected
    stream emit a line per milestone instead of one per step, which keeps
    log files readable.
    """

    BAR_WIDTH: Final[int] = 30
    LOG_PERCENT_STEP: Final[int] = 10
    LOG_COUNT_STEP: Final[int] = 100

    def format_line(self, settings: ProgressSettings, completed: int) -> str:
        """Render the bar as a single line without a terminator.

        Parameters
        ----------
        settings
            Rendering settings of the bar.
        completed
            Number of steps reported so far.

        Returns
        -------
        str
            The description, followed by a textual bar and the ratio when
            the total is known, or by the step count otherwise.
        """
        label = f"{settings.description}: " if settings.description else ""
        total = settings.total
        if total is None:
            return f"{label}{completed} {settings.unit}"
        ratio = 1.0 if total == 0 else min(completed / total, 1.0)
        filled = int(self.BAR_WIDTH * ratio)
        bar = "#" * filled + "-" * (self.BAR_WIDTH - filled)
        return f"{label}[{bar}] {ratio * 100:5.1f}% ({completed}/{total})"

    def milestone(self, settings: ProgressSettings, completed: int) -> int:
        """Index of the last milestone reached.

        Parameters
        ----------
        settings
            Rendering settings of the bar.
        completed
            Number of steps reported so far.

        Returns
        -------
        int
            Zero before the first milestone, increasing by one at each
            milestone.
        """
        total = settings.total
        if total is None:
            return completed // self.LOG_COUNT_STEP
        if total == 0:
            return 100 // self.LOG_PERCENT_STEP
        percent = completed * 100 // total
        return percent // self.LOG_PERCENT_STEP
