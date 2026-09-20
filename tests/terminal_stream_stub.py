"""Test double for an output stream attached to a terminal."""

from __future__ import annotations

from io import StringIO


class TerminalStreamStub(StringIO):
    """In-memory stream that reports itself as a terminal.

    Parameters
    ----------
    is_terminal
        Value returned by :meth:`isatty`.
    """

    def __init__(self, is_terminal: bool = True) -> None:
        super().__init__()
        self._is_terminal = is_terminal

    def isatty(self) -> bool:
        """Whether the stream pretends to be an interactive terminal."""
        return self._is_terminal
