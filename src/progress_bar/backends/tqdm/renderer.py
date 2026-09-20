"""Progress bar rendered with :mod:`tqdm`."""

from __future__ import annotations

from typing import Never

from tqdm.auto import tqdm

from progress_bar.backend import ProgressBarBackend
from progress_bar.environment import RenderEnvironment
from progress_bar.renderer import ProgressRenderer
from progress_bar.settings import ProgressSettings


class TqdmRenderer(ProgressRenderer):
    """Renderer using the ``tqdm`` package.

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
        self._bar: tqdm[Never] | None = None

    def _open(self) -> None:
        self._bar = tqdm(
            total=self._settings.total,
            desc=self._settings.description or None,
            unit=self._settings.unit,
            leave=self._settings.is_leave_visible,
            file=self._environment.stream,
        )

    def _render(self, step: int) -> None:
        if self._bar is None:
            raise RuntimeError("tqdm bar is not initialized")
        self._bar.update(step)

    def _close(self) -> None:
        if self._bar is None:
            return
        self._bar.close()
        self._bar = None

    @property
    def backend(self) -> ProgressBarBackend:
        """Backend implemented by this renderer."""
        return ProgressBarBackend.TQDM
