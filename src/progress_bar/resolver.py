"""Selection of the progress bar backend to use at runtime."""

from __future__ import annotations

from collections.abc import Sequence
from importlib.util import find_spec
from typing import Final

from progress_bar.backend import ProgressBarBackend
from progress_bar.environment import RenderEnvironment


class BackendResolver:
    """Picks an installed backend that suits the current environment.

    Parameters
    ----------
    environment
        Environment the bar is rendered in. A new
        :class:`~progress_bar.environment.RenderEnvironment` bound to
        ``sys.stderr`` is used when omitted.
    priority
        Backends tried in order during automatic resolution. Defaults to
        :attr:`DEFAULT_PRIORITY`.

    Raises
    ------
    ValueError
        If ``priority`` is empty.
    """

    DEFAULT_PRIORITY: Final[tuple[ProgressBarBackend, ...]] = (
        ProgressBarBackend.RICH,
        ProgressBarBackend.TQDM,
        ProgressBarBackend.ALIVE_PROGRESS,
        ProgressBarBackend.PROGRESSBAR2,
    )

    def __init__(
        self,
        environment: RenderEnvironment | None = None,
        priority: Sequence[ProgressBarBackend] | None = None,
    ) -> None:
        if priority is not None and len(priority) == 0:
            raise ValueError("priority must contain at least one backend")
        self._environment = RenderEnvironment() if environment is None else environment
        self._priority = tuple(self.DEFAULT_PRIORITY if priority is None else priority)
        self._installation_cache: dict[ProgressBarBackend, bool] = {}

    @property
    def environment(self) -> RenderEnvironment:
        """Environment the backends are resolved for."""
        return self._environment

    @property
    def priority(self) -> tuple[ProgressBarBackend, ...]:
        """Backends tried in order during automatic resolution."""
        return self._priority

    def is_installed(self, backend: ProgressBarBackend) -> bool:
        """Whether the package required by ``backend`` can be imported.

        Parameters
        ----------
        backend
            Backend to inspect.
        """
        if not backend.is_third_party:
            return True
        cached = self._installation_cache.get(backend)
        if cached is not None:
            return cached
        is_installed = find_spec(backend.module_name) is not None
        self._installation_cache[backend] = is_installed
        return is_installed

    def installed_backends(self) -> tuple[ProgressBarBackend, ...]:
        """Every backend that is importable in the current interpreter."""
        return tuple(
            backend for backend in ProgressBarBackend if self.is_installed(backend)
        )

    def resolve(
        self, preferred: ProgressBarBackend | None = None
    ) -> ProgressBarBackend:
        """Return the backend to render with.

        An installed ``preferred`` backend always wins. Otherwise the
        first installed backend of :attr:`priority` is used, and
        :attr:`ProgressBarBackend.PLAIN` serves as the last resort for
        redirected streams and environments without extra packages.

        Parameters
        ----------
        preferred
            Backend requested by the caller, or ``None`` to choose
            automatically.
        """
        if preferred is not None and self.is_installed(preferred):
            return preferred
        if not self._environment.is_rich_rendering_supported:
            return ProgressBarBackend.PLAIN
        for backend in self._priority:
            if self.is_installed(backend):
                return backend
        return ProgressBarBackend.PLAIN

    def require(self, backend: ProgressBarBackend) -> ProgressBarBackend:
        """Return ``backend`` and fail when its package is missing.

        Parameters
        ----------
        backend
            Backend that must be usable.

        Returns
        -------
        ProgressBarBackend
            The requested backend.

        Raises
        ------
        ModuleNotFoundError
            If the package required by ``backend`` is not installed.
        """
        if self.is_installed(backend):
            return backend
        raise ModuleNotFoundError(
            f"backend {backend.value} requires the package "
            + f"'{backend.distribution_name}'; install it with "
            + f"'pip install {backend.distribution_name}'"
        )
