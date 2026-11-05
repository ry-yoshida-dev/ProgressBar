"""State of one open bar of a group at one moment, for code reading it elsewhere."""

from __future__ import annotations

from dataclasses import dataclass

from progress_bar.settings import ProgressSettings


@dataclass(frozen=True, slots=True)
class ProgressBarSnapshot:
    """How far one open bar of a group is, read at one moment.

    A snapshot lets a thread other than the one doing the work, such as
    the handler of a request asking how far a task is, show the progress
    in its own way.

    Parameters
    ----------
    settings
        Rendering settings of the bar.
    completed
        Number of steps reported so far.
    elapsed_seconds
        Seconds since the bar was added.

    Raises
    ------
    ValueError
        If ``completed`` or ``elapsed_seconds`` is negative.
    """

    settings: ProgressSettings
    completed: int
    elapsed_seconds: float

    def __post_init__(self) -> None:
        if self.completed < 0:
            raise ValueError(f"completed must not be negative, got {self.completed}")
        if self.elapsed_seconds < 0:
            raise ValueError(
                f"elapsed_seconds must not be negative, got {self.elapsed_seconds}"
            )

    @property
    def fraction(self) -> float | None:
        """Share of the steps completed, from 0 to 1, or ``None`` without a total.

        An empty task counts as complete.
        """
        total = self.settings.total
        if total is None:
            return None
        if total == 0:
            return 1.0
        return min(self.completed / total, 1.0)

    def estimate_remaining_seconds(
        self, minimum_fraction: float = 0.0, minimum_elapsed_seconds: float = 0.0
    ) -> float | None:
        """Estimate the seconds left at the pace kept so far.

        Parameters
        ----------
        minimum_fraction
            Share of the steps that must be completed before an estimate
            is given, since the first steps tell the pace poorly.
        minimum_elapsed_seconds
            Seconds that must have passed before an estimate is given.

        Returns
        -------
        float | None
            The seconds left, or ``None`` without a total, before any step
            is completed, or before both minimums are reached.

        Raises
        ------
        ValueError
            If ``minimum_fraction`` is outside 0 to 1 or
            ``minimum_elapsed_seconds`` is negative.
        """
        if not 0.0 <= minimum_fraction <= 1.0:
            raise ValueError(
                f"minimum_fraction must be from 0 to 1, got {minimum_fraction}"
            )
        if minimum_elapsed_seconds < 0:
            raise ValueError(
                "minimum_elapsed_seconds must not be negative, "
                + f"got {minimum_elapsed_seconds}"
            )
        fraction = self.fraction
        if (
            fraction is None
            or self.completed == 0
            or fraction < minimum_fraction
            or self.elapsed_seconds < minimum_elapsed_seconds
        ):
            return None
        return self.elapsed_seconds / fraction * (1.0 - fraction)
