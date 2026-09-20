"""Detection of the runtime environment a progress bar is rendered in."""

from __future__ import annotations

import os
import sys
from typing import IO


class RenderEnvironment:
    """Terminal capabilities of the stream a progress bar writes to.

    Parameters
    ----------
    stream
        Output stream inspected for terminal capabilities. Defaults to
        :data:`sys.stderr`, which keeps the bar out of piped ``stdout``.
    """

    def __init__(self, stream: IO[str] | None = None) -> None:
        self._stream: IO[str] = sys.stderr if stream is None else stream

    @property
    def stream(self) -> IO[str]:
        """Stream the progress bar writes to."""
        return self._stream

    @property
    def is_terminal(self) -> bool:
        """Whether the stream is an interactive terminal."""
        try:
            return self._stream.isatty()
        except ValueError:
            return False

    @property
    def is_notebook(self) -> bool:
        """Whether the code runs inside an IPython kernel such as Jupyter."""
        ipython_module = sys.modules.get("IPython")
        if ipython_module is None:
            return False
        get_ipython = getattr(ipython_module, "get_ipython", None)
        if get_ipython is None:
            return False
        shell = get_ipython()
        return shell is not None and type(shell).__name__ == "ZMQInteractiveShell"

    @property
    def is_dumb_terminal(self) -> bool:
        """Whether ``TERM`` marks the terminal as incapable of redrawing."""
        return os.environ.get("TERM", "") == "dumb"

    @property
    def is_rich_rendering_supported(self) -> bool:
        """Whether animated, redrawing bars can be displayed."""
        if self.is_notebook:
            return True
        return self.is_terminal and not self.is_dumb_terminal
