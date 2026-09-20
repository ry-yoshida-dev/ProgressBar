"""Backends binding each optional library to the renderer interface.

Each backend lives in its own sub-package and imports its third-party
library at module level. The renderer classes are therefore exposed
lazily here, so importing this package never imports an optional library
that may not be installed.
"""

from typing import TYPE_CHECKING

from progress_bar.renderer import ProgressRenderer

if TYPE_CHECKING:
    from progress_bar.backends.alive_progress import AliveProgressRenderer
    from progress_bar.backends.plain import PlainRenderer
    from progress_bar.backends.progressbar2 import ProgressBar2Renderer
    from progress_bar.backends.rich import RichRenderer
    from progress_bar.backends.silent import SilentRenderer
    from progress_bar.backends.tqdm import TqdmRenderer

__all__ = [
    "AliveProgressRenderer",
    "PlainRenderer",
    "ProgressBar2Renderer",
    "RichRenderer",
    "SilentRenderer",
    "TqdmRenderer",
]


def __getattr__(name: str) -> type[ProgressRenderer]:
    """Import a renderer class on first access.

    Parameters
    ----------
    name
        Name of the renderer class to import.

    Returns
    -------
    type[ProgressRenderer]
        The requested renderer class.

    Raises
    ------
    AttributeError
        If ``name`` is not a renderer of this package.
    """
    match name:
        case "TqdmRenderer":
            from progress_bar.backends.tqdm import TqdmRenderer

            return TqdmRenderer
        case "ProgressBar2Renderer":
            from progress_bar.backends.progressbar2 import ProgressBar2Renderer

            return ProgressBar2Renderer
        case "AliveProgressRenderer":
            from progress_bar.backends.alive_progress import AliveProgressRenderer

            return AliveProgressRenderer
        case "RichRenderer":
            from progress_bar.backends.rich import RichRenderer

            return RichRenderer
        case "PlainRenderer":
            from progress_bar.backends.plain import PlainRenderer

            return PlainRenderer
        case "SilentRenderer":
            from progress_bar.backends.silent import SilentRenderer

            return SilentRenderer
        case _:
            raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
