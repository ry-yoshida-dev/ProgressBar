"""Call signature of the handle yielded by ``alive_progress``."""

from __future__ import annotations

from typing import Protocol


class AliveBarHandle(Protocol):
    """Callable handed out by ``alive_bar`` to report completed steps.

    ``alive_progress`` does not annotate the yielded handle, so this
    protocol pins down the part of its call signature that is used here.
    """

    def __call__(self, count: int = 1, /) -> None:
        """Advance the bar.

        Parameters
        ----------
        count
            Number of steps completed since the previous call.
        """
        ...
