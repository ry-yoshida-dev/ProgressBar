"""Construction of group renderers for a concrete backend."""

from __future__ import annotations

from progress_bar.backend import ProgressBarBackend
from progress_bar.environment import RenderEnvironment
from progress_bar.group.renderer import ProgressGroupRenderer


class GroupRendererFactory:
    """Creates the group renderer implementing a given backend.

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

    def create(self, backend: ProgressBarBackend) -> ProgressGroupRenderer:
        """Build a group renderer for ``backend``.

        Parameters
        ----------
        backend
            Backend to render with.

        Returns
        -------
        ProgressGroupRenderer
            Renderer that has not been started yet.

        Raises
        ------
        ValueError
            If ``backend`` cannot display several bars at once.
        ModuleNotFoundError
            If the package required by ``backend`` is not installed.
        """
        match backend:
            case ProgressBarBackend.TQDM:
                from progress_bar.backends.tqdm import TqdmGroupRenderer

                return TqdmGroupRenderer(self._environment)
            case ProgressBarBackend.PROGRESSBAR2:
                from progress_bar.backends.progressbar2 import (
                    ProgressBar2GroupRenderer,
                )

                return ProgressBar2GroupRenderer(self._environment)
            case ProgressBarBackend.RICH:
                from progress_bar.backends.rich import RichGroupRenderer

                return RichGroupRenderer(self._environment)
            case ProgressBarBackend.PLAIN:
                from progress_bar.backends.plain import PlainGroupRenderer

                return PlainGroupRenderer(self._environment)
            case ProgressBarBackend.SILENT:
                from progress_bar.backends.silent import SilentGroupRenderer

                return SilentGroupRenderer(self._environment)
            case ProgressBarBackend.ALIVE_PROGRESS:
                raise ValueError(
                    f"backend {backend.value} cannot display several bars at once"
                )

    @property
    def environment(self) -> RenderEnvironment:
        """Environment passed to every created renderer."""
        return self._environment
