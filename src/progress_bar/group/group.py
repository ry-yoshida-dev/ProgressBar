"""Several progress bars displayed together, from threads or processes."""

from __future__ import annotations

import multiprocessing
import threading
from multiprocessing.context import BaseContext
from multiprocessing.queues import Queue
from types import TracebackType

from progress_bar.backend import ProgressBarBackend
from progress_bar.environment import RenderEnvironment
from progress_bar.group.bar import GroupedProgressBar
from progress_bar.group.factory import GroupRendererFactory
from progress_bar.group.remote.event import RemoteBarEvent
from progress_bar.group.remote.group import RemoteProgressBarGroup
from progress_bar.group.remote.listener import RemoteEventListener
from progress_bar.group.renderer import ProgressGroupRenderer
from progress_bar.group.source import ProgressBarSource
from progress_bar.resolver import BackendResolver
from progress_bar.settings import ProgressSettings


class ProgressBarGroup(ProgressBarSource):
    """Bars that run side by side, drawn by one backend without clashing.

    Every bar is added while the group is displayed and appears on a line
    of its own. The group serializes the calls of its bars, so they can be
    advanced from different threads, and :meth:`remote` extends it to
    worker processes. Finishing the group finishes every bar still open.

    Parameters
    ----------
    backend
        Backend requested by the caller, or ``None`` to choose the best
        installed one. A backend that cannot display several bars at once
        is replaced by the automatic choice, with a warning.
    is_enabled
        Whether progress is displayed at all. When ``False`` the silent
        backend is used, no output is produced, and :meth:`remote` hands
        out bars that send nothing.
    environment
        Environment the bars are rendered in.
    context
        Multiprocessing context the queue of :meth:`remote` is created
        with. Use the context of the worker processes when it is not the
        default one.

    Examples
    --------
    >>> with ProgressBarGroup() as group:
    ...     for scene in group.report(scenes, description="Scenes"):
    ...         cameras = {
    ...             camera: group.add(total=100, description=camera,
    ...                               is_leave_visible=False)
    ...             for camera in scene.cameras
    ...         }
    """

    def __init__(
        self,
        *,
        backend: ProgressBarBackend | None = None,
        is_enabled: bool = True,
        environment: RenderEnvironment | None = None,
        context: BaseContext | None = None,
    ) -> None:
        self._environment = RenderEnvironment() if environment is None else environment
        self._resolver = BackendResolver(self._environment)
        self._factory = GroupRendererFactory(self._environment)
        self._context = multiprocessing.get_context() if context is None else context
        self._backend = (
            self._resolver.resolve_group(backend)
            if is_enabled
            else ProgressBarBackend.SILENT
        )
        self._lock = threading.RLock()
        self._renderer: ProgressGroupRenderer | None = None
        self._listener: RemoteEventListener | None = None
        self._added_bar_count = 0

    def start(self) -> None:
        """Display the group, initially without any bar.

        Raises
        ------
        RuntimeError
            If the group is already displayed.
        """
        with self._lock:
            if self._renderer is not None:
                raise RuntimeError("the group is already started")
            renderer = self._factory.create(self._backend)
            renderer.start()
            self._renderer = renderer

    def finish(self) -> None:
        """Finish every open bar and close the group, ignoring an idle group.

        Events already sent by worker processes are applied first.
        """
        listener = self._listener
        if listener is not None:
            listener.stop()
            self._listener = None
        with self._lock:
            renderer = self._renderer
            if renderer is None:
                return
            self._renderer = None
            renderer.finish()

    def add(
        self,
        total: int | None = None,
        description: str = "",
        *,
        unit: str = "it",
        is_leave_visible: bool = True,
    ) -> GroupedProgressBar:
        """Display a new bar in the group.

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

        Returns
        -------
        GroupedProgressBar
            The running bar.

        Raises
        ------
        ValueError
            If ``total`` is negative or ``unit`` is empty.
        RuntimeError
            If the group is not displayed.
        """
        settings = ProgressSettings(
            total=total,
            description=description,
            unit=unit,
            is_leave_visible=is_leave_visible,
        )
        with self._lock:
            renderer = self._require_renderer()
            key = f"local-{self._added_bar_count}"
            self._added_bar_count += 1
            renderer.add_bar(key, settings)
        return GroupedProgressBar(self, key, settings)

    def remote(self) -> RemoteProgressBarGroup:
        """Return a proxy through which worker processes add bars here.

        The first call starts a thread that applies the events of the
        workers, and later calls share it. Pass the proxy to a worker when
        the process is created, as described in
        :class:`~progress_bar.RemoteProgressBarGroup`.

        Returns
        -------
        RemoteProgressBarGroup
            Proxy to hand to worker processes.

        Raises
        ------
        RuntimeError
            If the group is not displayed.
        """
        with self._lock:
            self._require_renderer()
            if self._backend is ProgressBarBackend.SILENT:
                return RemoteProgressBarGroup(None)
            if self._listener is None:
                queue: Queue[RemoteBarEvent | None] = self._context.Queue()
                listener = RemoteEventListener(queue, self)
                listener.start()
                self._listener = listener
            return RemoteProgressBarGroup(self._listener.queue)

    def open_bar(self, key: str, settings: ProgressSettings) -> None:
        """Display a bar announced by a worker process.

        A key that is already open, or a group that is not displayed, is
        ignored.

        Parameters
        ----------
        key
            Identifier of the bar.
        settings
            Rendering settings of the bar.
        """
        with self._lock:
            renderer = self._renderer
            if renderer is None or renderer.is_open(key):
                return
            renderer.add_bar(key, settings)

    def advance_bar(self, key: str, step: int) -> None:
        """Advance one bar, ignoring a key the group does not display.

        Parameters
        ----------
        key
            Identifier of the bar.
        step
            Number of steps completed since the previous call.
        """
        with self._lock:
            renderer = self._renderer
            if renderer is None or not renderer.is_open(key):
                return
            renderer.advance_bar(key, step)

    def finish_bar(self, key: str) -> None:
        """Finalize one bar, ignoring a key the group does not display.

        Parameters
        ----------
        key
            Identifier of the bar.
        """
        with self._lock:
            if self._renderer is not None:
                self._renderer.finish_bar(key)

    def __enter__(self) -> ProgressBarGroup:
        self.start()
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.finish()

    def _require_renderer(self) -> ProgressGroupRenderer:
        if self._renderer is None:
            raise RuntimeError("the group is not started; call start() first")
        return self._renderer

    @property
    def backend(self) -> ProgressBarBackend:
        """Backend the group is rendered with."""
        return self._backend

    @property
    def is_active(self) -> bool:
        """Whether the group is currently displayed."""
        return self._renderer is not None

    @property
    def installed_backends(self) -> tuple[ProgressBarBackend, ...]:
        """Backends whose packages are importable in this interpreter."""
        return self._resolver.installed_backends()
