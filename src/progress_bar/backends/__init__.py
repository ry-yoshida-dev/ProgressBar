"""Backends binding each optional library to the renderer interface.

Each backend lives in its own sub-package and imports its third-party
library at module level. The renderer classes are therefore exposed
lazily here, so importing this package never imports an optional library
that may not be installed.
"""

from typing import TYPE_CHECKING

from progress_bar.group.renderer import ProgressGroupRenderer
from progress_bar.renderer import ProgressRenderer

if TYPE_CHECKING:
    from progress_bar.backends.alive_progress import AliveProgressRenderer
    from progress_bar.backends.plain import PlainGroupRenderer, PlainRenderer
    from progress_bar.backends.progressbar2 import (
        ProgressBar2GroupRenderer,
        ProgressBar2Renderer,
    )
    from progress_bar.backends.rich import RichGroupRenderer, RichRenderer
    from progress_bar.backends.silent import SilentGroupRenderer, SilentRenderer
    from progress_bar.backends.tqdm import TqdmGroupRenderer, TqdmRenderer

__all__ = [
    "AliveProgressRenderer",
    "PlainGroupRenderer",
    "PlainRenderer",
    "ProgressBar2GroupRenderer",
    "ProgressBar2Renderer",
    "RichGroupRenderer",
    "RichRenderer",
    "SilentGroupRenderer",
    "SilentRenderer",
    "TqdmGroupRenderer",
    "TqdmRenderer",
]


def __getattr__(name: str) -> type[ProgressRenderer] | type[ProgressGroupRenderer]:
    """Import a renderer class on first access.

    Parameters
    ----------
    name
        Name of the renderer class to import.

    Returns
    -------
    type[ProgressRenderer] | type[ProgressGroupRenderer]
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
        case "TqdmGroupRenderer":
            from progress_bar.backends.tqdm import TqdmGroupRenderer

            return TqdmGroupRenderer
        case "ProgressBar2GroupRenderer":
            from progress_bar.backends.progressbar2 import ProgressBar2GroupRenderer

            return ProgressBar2GroupRenderer
        case "RichGroupRenderer":
            from progress_bar.backends.rich import RichGroupRenderer

            return RichGroupRenderer
        case "PlainGroupRenderer":
            from progress_bar.backends.plain import PlainGroupRenderer

            return PlainGroupRenderer
        case "SilentGroupRenderer":
            from progress_bar.backends.silent import SilentGroupRenderer

            return SilentGroupRenderer
        case _:
            raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
