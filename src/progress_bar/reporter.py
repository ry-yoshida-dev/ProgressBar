"""High level entry point for reporting progress."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sized
from dataclasses import replace
from types import TracebackType

from progress_bar.backend import ProgressBarBackend
from progress_bar.environment import RenderEnvironment
from progress_bar.factory import RendererFactory
from progress_bar.renderer import ProgressRenderer
from progress_bar.resolver import BackendResolver
from progress_bar.settings import ProgressSettings


class ProgressBarReporter:
    """Progress bar whose backend is chosen at runtime.

    The reporter resolves a backend once on creation, builds the matching
    renderer when the task starts, and can be reused for several tasks.

    Parameters
    ----------
    total
        Number of steps of the task, or ``None`` when unknown.
    description
        Label rendered next to the bar.
    unit
        Name of a single step.
    is_leave_visible
        Whether the finished bar stays on screen.
    backend
        Backend requested by the caller, or ``None`` to choose the best
        one available.
    is_enabled
        Whether progress is displayed at all. When ``False`` the silent
        backend is used and no output is produced.
    environment
        Environment the bar is rendered in.

    Examples
    --------
    >>> with ProgressBarReporter(total=3, description="Loading") as reporter:
    ...     for _ in range(3):
    ...         reporter.advance()
    """

    def __init__(
        self,
        total: int | None = None,
        description: str = "",
        *,
        unit: str = "it",
        is_leave_visible: bool = True,
        backend: ProgressBarBackend | None = None,
        is_enabled: bool = True,
        environment: RenderEnvironment | None = None,
    ) -> None:
        self._settings = ProgressSettings(
            total=total,
            description=description,
            unit=unit,
            is_leave_visible=is_leave_visible,
        )
        self._environment = RenderEnvironment() if environment is None else environment
        self._resolver = BackendResolver(self._environment)
        self._factory = RendererFactory(self._environment)
        self._is_enabled = is_enabled
        self._renderer: ProgressRenderer | None = None
        self._backend = self._select(backend)

    @classmethod
    def from_settings(
        cls,
        settings: ProgressSettings,
        *,
        backend: ProgressBarBackend | None = None,
        is_enabled: bool = True,
        environment: RenderEnvironment | None = None,
    ) -> ProgressBarReporter:
        """Build a reporter from an existing settings object.

        Parameters
        ----------
        settings
            Rendering settings of the task to display.
        backend
            Backend requested by the caller, or ``None`` for automatic
            selection.
        is_enabled
            Whether progress is displayed at all.
        environment
            Environment the bar is rendered in.

        Returns
        -------
        ProgressBarReporter
            Reporter configured with ``settings``.
        """
        return cls(
            total=settings.total,
            description=settings.description,
            unit=settings.unit,
            is_leave_visible=settings.is_leave_visible,
            backend=backend,
            is_enabled=is_enabled,
            environment=environment,
        )

    def start(self) -> None:
        """Display the bar of a new task.

        Raises
        ------
        RuntimeError
            If a task is already running.
        """
        if self._renderer is not None:
            raise RuntimeError("a task is already running")
        renderer = self._factory.create(self._backend, self._settings)
        renderer.start()
        self._renderer = renderer

    def advance(self, step: int = 1) -> None:
        """Record completed steps.

        Parameters
        ----------
        step
            Number of steps completed since the previous call. Zero is
            accepted and leaves the bar untouched.

        Raises
        ------
        ValueError
            If ``step`` is negative.
        RuntimeError
            If no task is running.
        """
        if self._renderer is None:
            raise RuntimeError("no task is running; call start() first")
        self._renderer.advance(step)

    def finish(self) -> None:
        """Finalize the running task, ignoring an idle reporter."""
        if self._renderer is None:
            return
        renderer = self._renderer
        self._renderer = None
        renderer.finish()

    def report[ItemT](self, iterable: Iterable[ItemT]) -> Iterator[ItemT]:
        """Yield the items of ``iterable`` while advancing the bar.

        The task is started and finished automatically unless it is
        already running. When the total is unknown and ``iterable`` has a
        length, that length becomes the total.

        Parameters
        ----------
        iterable
            Items to iterate over.

        Yields
        ------
        ItemT
            The items of ``iterable``, unchanged.
        """
        if self._renderer is None:
            self._adopt_length_of(iterable)
        is_owned_task = self._renderer is None
        if is_owned_task:
            self.start()
        try:
            for item in iterable:
                yield item
                self.advance()
        finally:
            if is_owned_task:
                self.finish()

    def switch_to(self, backend: ProgressBarBackend | None) -> ProgressBarBackend:
        """Change the backend used for the next task.

        Parameters
        ----------
        backend
            Backend to switch to, or ``None`` to resolve automatically.

        Returns
        -------
        ProgressBarBackend
            Backend that will actually be used, which differs from
            ``backend`` when its package is missing.

        Raises
        ------
        RuntimeError
            If a task is currently running.
        """
        if self._renderer is not None:
            raise RuntimeError("cannot switch backend while a task is running")
        self._backend = self._select(backend)
        return self._backend

    def __enter__(self) -> ProgressBarReporter:
        self.start()
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.finish()

    @property
    def backend(self) -> ProgressBarBackend:
        """Backend the next task is rendered with."""
        return self._backend

    @property
    def settings(self) -> ProgressSettings:
        """Rendering settings of the task."""
        return self._settings

    @property
    def is_active(self) -> bool:
        """Whether a task is currently displayed."""
        return self._renderer is not None

    @property
    def completed(self) -> int:
        """Number of steps reported for the running task."""
        return 0 if self._renderer is None else self._renderer.completed

    @property
    def installed_backends(self) -> tuple[ProgressBarBackend, ...]:
        """Backends whose packages are importable in this interpreter."""
        return self._resolver.installed_backends()

    def _select(self, backend: ProgressBarBackend | None) -> ProgressBarBackend:
        if not self._is_enabled:
            return ProgressBarBackend.SILENT
        return self._resolver.resolve(backend)

    def _adopt_length_of(self, iterable: Iterable[object]) -> None:
        if self._settings.total is not None or not isinstance(iterable, Sized):
            return
        self._settings = replace(self._settings, total=len(iterable))
