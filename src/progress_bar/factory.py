"""Construction of reporters for a concrete backend."""

from __future__ import annotations

from progress_bar.backend import ProgressBarBackend
from progress_bar.environment import RenderEnvironment
from progress_bar.reporter import ProgressReporter
from progress_bar.settings import ProgressSettings


class ReporterFactory:
    """Creates the reporter implementing a given backend.

    Adapter modules are imported on demand so that an uninstalled
    optional package never breaks an unrelated backend.

    Parameters
    ----------
    environment
        Environment passed to every created reporter. A new
        :class:`~progress_bar.environment.RenderEnvironment` bound to
        ``sys.stderr`` is used when omitted.
    """

    def __init__(self, environment: RenderEnvironment | None = None) -> None:
        self._environment = RenderEnvironment() if environment is None else environment

    @property
    def environment(self) -> RenderEnvironment:
        """Environment passed to every created reporter."""
        return self._environment

    def create(
        self, backend: ProgressBarBackend, settings: ProgressSettings
    ) -> ProgressReporter:
        """Build a reporter for ``backend``.

        Parameters
        ----------
        backend
            Backend to render with.
        settings
            Rendering settings of the task to display.

        Returns
        -------
        ProgressReporter
            Reporter that has not been started yet.

        Raises
        ------
        ModuleNotFoundError
            If the package required by ``backend`` is not installed.
        """
        match backend:
            case ProgressBarBackend.TQDM:
                from progress_bar.backends.tqdm import TqdmAdapter

                return TqdmAdapter(settings, self._environment)
            case ProgressBarBackend.PROGRESSBAR2:
                from progress_bar.backends.progressbar2 import ProgressBar2Adapter

                return ProgressBar2Adapter(settings, self._environment)
            case ProgressBarBackend.ALIVE_PROGRESS:
                from progress_bar.backends.alive_progress import AliveProgressAdapter

                return AliveProgressAdapter(settings, self._environment)
            case ProgressBarBackend.RICH:
                from progress_bar.backends.rich import RichAdapter

                return RichAdapter(settings, self._environment)
            case ProgressBarBackend.PLAIN:
                from progress_bar.backends.plain import PlainAdapter

                return PlainAdapter(settings, self._environment)
            case ProgressBarBackend.SILENT:
                from progress_bar.backends.silent import SilentAdapter

                return SilentAdapter(settings, self._environment)
