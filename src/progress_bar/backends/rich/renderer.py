"""Progress bar rendered with :mod:`rich.progress`."""

from __future__ import annotations

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)

from progress_bar.backend import ProgressBarBackend
from progress_bar.environment import RenderEnvironment
from progress_bar.renderer import ProgressRenderer
from progress_bar.settings import ProgressSettings


class RichRenderer(ProgressRenderer):
    """Renderer using the ``rich`` package.

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
        self._progress: Progress | None = None
        self._task_id: TaskID | None = None

    def _open(self) -> None:
        progress = Progress(
            *self._build_columns(),
            console=Console(file=self._environment.stream),
            transient=not self._settings.is_leave_visible,
        )
        progress.start()
        self._task_id = progress.add_task(
            self._settings.description or "working",
            total=self._settings.total,
        )
        self._progress = progress

    def _render(self, step: int) -> None:
        if self._progress is None or self._task_id is None:
            raise RuntimeError("rich progress is not initialized")
        self._progress.advance(self._task_id, step)

    def _close(self) -> None:
        if self._progress is None:
            return
        self._progress.stop()
        self._progress = None
        self._task_id = None

    def _build_columns(self) -> tuple[ProgressColumn, ...]:
        description_column = TextColumn("[progress.description]{task.description}")
        if self._settings.total is None:
            return (SpinnerColumn(), description_column, TextColumn("{task.completed}"))
        return (
            description_column,
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
        )

    @property
    def backend(self) -> ProgressBarBackend:
        """Backend implemented by this renderer."""
        return ProgressBarBackend.RICH
