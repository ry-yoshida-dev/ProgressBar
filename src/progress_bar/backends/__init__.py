"""Backends binding each optional library to the reporter interface.

Each backend lives in its own sub-package and imports its third-party
library at module level. The adapter classes are therefore exposed
lazily here, so importing this package never imports an optional library
that may not be installed.
"""

from typing import TYPE_CHECKING

from progress_bar.reporter import ProgressReporter

if TYPE_CHECKING:
    from progress_bar.backends.alive_progress import AliveProgressAdapter
    from progress_bar.backends.plain import PlainAdapter
    from progress_bar.backends.progressbar2 import ProgressBar2Adapter
    from progress_bar.backends.rich import RichAdapter
    from progress_bar.backends.silent import SilentAdapter
    from progress_bar.backends.tqdm import TqdmAdapter

__all__ = [
    "AliveProgressAdapter",
    "PlainAdapter",
    "ProgressBar2Adapter",
    "RichAdapter",
    "SilentAdapter",
    "TqdmAdapter",
]


def __getattr__(name: str) -> type[ProgressReporter]:
    """Import an adapter class on first access.

    Parameters
    ----------
    name
        Name of the adapter class to import.

    Returns
    -------
    type[ProgressReporter]
        The requested adapter class.

    Raises
    ------
    AttributeError
        If ``name`` is not an adapter of this package.
    """
    match name:
        case "TqdmAdapter":
            from progress_bar.backends.tqdm import TqdmAdapter

            return TqdmAdapter
        case "ProgressBar2Adapter":
            from progress_bar.backends.progressbar2 import ProgressBar2Adapter

            return ProgressBar2Adapter
        case "AliveProgressAdapter":
            from progress_bar.backends.alive_progress import AliveProgressAdapter

            return AliveProgressAdapter
        case "RichAdapter":
            from progress_bar.backends.rich import RichAdapter

            return RichAdapter
        case "PlainAdapter":
            from progress_bar.backends.plain import PlainAdapter

            return PlainAdapter
        case "SilentAdapter":
            from progress_bar.backends.silent import SilentAdapter

            return SilentAdapter
        case _:
            raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
