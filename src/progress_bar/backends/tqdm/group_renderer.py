"""Group of progress bars rendered with :mod:`tqdm`."""

from __future__ import annotations

from typing import Never

from tqdm.auto import tqdm

from progress_bar.backend import ProgressBarBackend
from progress_bar.environment import RenderEnvironment
from progress_bar.group.renderer import ProgressGroupRenderer
from progress_bar.settings import ProgressSettings


class TqdmGroupRenderer(ProgressGroupRenderer):
    """Group renderer giving every bar its own ``tqdm`` line.

    Each bar is placed on the lowest line that no other bar occupies, so a
    finished bar frees its line for the next one. ``tqdm`` writes the
    final state of a bar it leaves on screen at the cursor rather than on
    the bar's own line, so a finished bar that stays visible is cleared
    instead, and its final line is written above the running bars with
    ``tqdm.write``.

    Parameters
    ----------
    environment
        Output stream and terminal capabilities to render with.
    """

    def __init__(self, environment: RenderEnvironment) -> None:
        super().__init__(environment)
        self._bar_by_key: dict[str, tqdm[Never]] = {}
        self._position_by_key: dict[str, int] = {}

    def _open(self) -> None:
        return

    def _add_bar(self, key: str, settings: ProgressSettings) -> None:
        position = self._lowest_free_position()
        self._position_by_key[key] = position
        self._bar_by_key[key] = tqdm(
            total=settings.total,
            desc=settings.description or None,
            unit=settings.unit,
            leave=False,
            position=position,
            file=self._environment.stream,
        )

    def _render_bar(self, key: str, step: int) -> None:
        self._bar_by_key[key].update(step)

    def _finish_bar(self, key: str) -> None:
        bar = self._bar_by_key.pop(key)
        del self._position_by_key[key]
        final_line = str(bar)
        bar.close()
        if self._settings_by_key[key].is_leave_visible:
            tqdm.write(f"\r{final_line}", file=self._environment.stream)

    def _close(self) -> None:
        return

    def _lowest_free_position(self) -> int:
        occupied = set(self._position_by_key.values())
        position = 0
        while position in occupied:
            position += 1
        return position

    @property
    def backend(self) -> ProgressBarBackend:
        """Backend implemented by this renderer."""
        return ProgressBarBackend.TQDM
