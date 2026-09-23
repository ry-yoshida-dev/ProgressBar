"""Group of progress bars rendered with :mod:`rich.progress`."""

from __future__ import annotations

from rich.console import Console
from rich.markup import escape
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)

from progress_bar.backend import ProgressBarBackend
from progress_bar.environment import RenderEnvironment
from progress_bar.group.renderer import ProgressGroupRenderer
from progress_bar.settings import ProgressSettings


class RichGroupRenderer(ProgressGroupRenderer):
    """Group renderer drawing every bar as a task of one ``rich`` display.

    ``rich`` allows a single live display per console, so the whole group
    shares one :class:`rich.progress.Progress`. A finished bar that stays
    visible remains as a completed task, and any other bar is removed.

    Parameters
    ----------
    environment
        Output stream and terminal capabilities to render with.
    """

    def __init__(self, environment: RenderEnvironment) -> None:
        super().__init__(environment)
        self._progress: Progress | None = None
        self._task_id_by_key: dict[str, TaskID] = {}

    def _open(self) -> None:
        progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
            console=Console(file=self._environment.stream),
        )
        progress.start()
        self._progress = progress

    def _add_bar(self, key: str, settings: ProgressSettings) -> None:
        self._task_id_by_key[key] = self._require_progress().add_task(
            escape(settings.description or "working"),
            total=settings.total,
        )

    def _render_bar(self, key: str, step: int) -> None:
        self._require_progress().advance(self._task_id_by_key[key], step)

    def _finish_bar(self, key: str) -> None:
        task_id = self._task_id_by_key.pop(key)
        if not self._settings_by_key[key].is_leave_visible:
            self._require_progress().remove_task(task_id)

    def _close(self) -> None:
        if self._progress is None:
            return
        self._progress.stop()
        self._progress = None

    def _require_progress(self) -> Progress:
        if self._progress is None:
            raise RuntimeError("rich progress is not initialized")
        return self._progress

    @property
    def backend(self) -> ProgressBarBackend:
        """Backend implemented by this renderer."""
        return ProgressBarBackend.RICH
