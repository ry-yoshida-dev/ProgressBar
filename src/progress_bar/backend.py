"""Backend identifiers for the supported progress bar implementations."""

from __future__ import annotations

from enum import Enum


class ProgressBarBackend(Enum):
    """Progress bar implementation that can render a running task.

    Each member maps to an optional third-party package, except for the
    dependency-free members :attr:`PLAIN` and :attr:`SILENT`.
    """

    TQDM = "tqdm"
    PROGRESSBAR2 = "progressbar2"
    ALIVE_PROGRESS = "alive_progress"
    RICH = "rich"
    PLAIN = "plain"
    SILENT = "silent"

    @property
    def module_name(self) -> str:
        """Top-level module that must be importable to use the backend.

        Returns
        -------
        str
            Importable module name, or an empty string for backends that
            do not rely on a third-party package.
        """
        match self:
            case ProgressBarBackend.TQDM:
                return "tqdm"
            case ProgressBarBackend.PROGRESSBAR2:
                return "progressbar"
            case ProgressBarBackend.ALIVE_PROGRESS:
                return "alive_progress"
            case ProgressBarBackend.RICH:
                return "rich"
            case ProgressBarBackend.PLAIN | ProgressBarBackend.SILENT:
                return ""

    @property
    def distribution_name(self) -> str:
        """Name used to install the backend with a package manager.

        Returns
        -------
        str
            Distribution name, or an empty string for built-in backends.
        """
        match self:
            case ProgressBarBackend.TQDM:
                return "tqdm"
            case ProgressBarBackend.PROGRESSBAR2:
                return "progressbar2"
            case ProgressBarBackend.ALIVE_PROGRESS:
                return "alive-progress"
            case ProgressBarBackend.RICH:
                return "rich"
            case ProgressBarBackend.PLAIN | ProgressBarBackend.SILENT:
                return ""

    @property
    def is_third_party(self) -> bool:
        """Whether the backend needs an external package to be installed."""
        return self.module_name != ""
