"""Construction of renderers for a concrete backend."""

from __future__ import annotations

from progress_bar.backend import ProgressBarBackend
from progress_bar.environment import RenderEnvironment
from progress_bar.renderer import ProgressRenderer
from progress_bar.settings import ProgressSettings


class RendererFactory:
    """Creates the renderer implementing a given backend.

    Renderer modules are imported on demand so that an uninstalled
    optional package never breaks an unrelated backend.

    Parameters
    ----------
    environment
        Environment passed to every created renderer. A new
        :class:`~progress_bar.environment.RenderEnvironment` bound to
        ``sys.stderr`` is used when omitted.
    """

    def __init__(self, environment: RenderEnvironment | None = None) -> None:
        self._environment = RenderEnvironment() if environment is None else environment

    def create(
        self, backend: ProgressBarBackend, settings: ProgressSettings
    ) -> ProgressRenderer:
        """Build a renderer for ``backend``.

        Parameters
        ----------
        backend
            Backend to render with.
        settings
            Rendering settings of the task to display.

        Returns
        -------
        ProgressRenderer
            Renderer that has not been started yet.

        Raises
        ------
        ModuleNotFoundError
            If the package required by ``backend`` is not installed.
        """
        match backend:
            case ProgressBarBackend.TQDM:
                from progress_bar.backends.tqdm import TqdmRenderer

                return TqdmRenderer(settings, self._environment)
            case ProgressBarBackend.PROGRESSBAR2:
                from progress_bar.backends.progressbar2 import ProgressBar2Renderer

                return ProgressBar2Renderer(settings, self._environment)
            case ProgressBarBackend.ALIVE_PROGRESS:
                from progress_bar.backends.alive_progress import AliveProgressRenderer

                return AliveProgressRenderer(settings, self._environment)
            case ProgressBarBackend.RICH:
                from progress_bar.backends.rich import RichRenderer

                return RichRenderer(settings, self._environment)
            case ProgressBarBackend.PLAIN:
                from progress_bar.backends.plain import PlainRenderer

                return PlainRenderer(settings, self._environment)
            case ProgressBarBackend.SILENT:
                from progress_bar.backends.silent import SilentRenderer

                return SilentRenderer(settings, self._environment)

    @property
    def environment(self) -> RenderEnvironment:
        """Environment passed to every created renderer."""
        return self._environment
