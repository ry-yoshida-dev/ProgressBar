"""Backend-independent rendering of several concurrent progress bars."""

from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType

from progress_bar.backend import ProgressBarBackend
from progress_bar.environment import RenderEnvironment
from progress_bar.settings import ProgressSettings


class ProgressGroupRenderer(ABC):
    """Lifecycle of a group of bars displayed together by one backend.

    Every bar of the group is identified by a key chosen by the caller.
    Bars can be added and finished at any time while the group is
    displayed, and finishing the group finishes every bar still open.

    Concrete subclasses adapt one third-party library by implementing
    :meth:`_open`, :meth:`_add_bar`, :meth:`_render_bar`,
    :meth:`_finish_bar` and :meth:`_close`. A renderer is not thread-safe;
    :class:`~progress_bar.ProgressBarGroup` serializes every call to it.

    Parameters
    ----------
    environment
        Output stream and terminal capabilities to render with.
    """

    def __init__(self, environment: RenderEnvironment) -> None:
        self._environment = environment
        self._settings_by_key: dict[str, ProgressSettings] = {}
        self._completed_by_key: dict[str, int] = {}
        self._is_active = False

    def start(self) -> None:
        """Display the group, initially without any bar.

        Raises
        ------
        RuntimeError
            If the group is already displayed.
        """
        if self._is_active:
            raise RuntimeError(f"{type(self).__name__} is already started")
        self._open()
        self._is_active = True

    def add_bar(self, key: str, settings: ProgressSettings) -> None:
        """Display a new bar in the group.

        Parameters
        ----------
        key
            Identifier of the bar, unique among the open bars of the group.
        settings
            Rendering settings of the bar.

        Raises
        ------
        RuntimeError
            If the group is not displayed.
        ValueError
            If a bar with the same key is already open.
        """
        self._require_active()
        if key in self._settings_by_key:
            raise ValueError(f"a bar with key {key!r} is already open")
        self._settings_by_key[key] = settings
        self._completed_by_key[key] = 0
        self._add_bar(key, settings)

    def advance_bar(self, key: str, step: int = 1) -> None:
        """Report completed steps of one bar.

        Parameters
        ----------
        key
            Identifier of the bar.
        step
            Number of steps completed since the previous call. Zero is
            accepted and leaves the bar untouched.

        Raises
        ------
        ValueError
            If ``step`` is negative.
        RuntimeError
            If the group is not displayed.
        KeyError
            If no open bar has the key.
        """
        if step < 0:
            raise ValueError(f"step must not be negative, got {step}")
        self._require_active()
        if key not in self._settings_by_key:
            raise KeyError(f"no open bar has key {key!r}")
        if step == 0:
            return
        self._completed_by_key[key] += step
        self._render_bar(key, step)

    def finish_bar(self, key: str) -> None:
        """Finalize one bar, ignoring a key that is not open.

        A bar whose settings ask to stay visible keeps its final state on
        screen, and any other bar is removed from the display.

        Parameters
        ----------
        key
            Identifier of the bar.
        """
        if not self._is_active or key not in self._settings_by_key:
            return
        self._finish_bar(key)
        del self._settings_by_key[key]
        del self._completed_by_key[key]

    def finish(self) -> None:
        """Finish every open bar and close the group, ignoring an idle group."""
        if not self._is_active:
            return
        for key in list(self._settings_by_key):
            self.finish_bar(key)
        self._is_active = False
        self._close()

    def is_open(self, key: str) -> bool:
        """Whether a bar with the key is open in the group.

        Parameters
        ----------
        key
            Identifier of the bar.
        """
        return key in self._settings_by_key

    def completed_of(self, key: str) -> int:
        """Number of steps reported so far for one open bar.

        Parameters
        ----------
        key
            Identifier of the bar.

        Raises
        ------
        KeyError
            If no open bar has the key.
        """
        return self._completed_by_key[key]

    def __enter__(self) -> ProgressGroupRenderer:
        self.start()
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.finish()

    def _require_active(self) -> None:
        if not self._is_active:
            raise RuntimeError(f"{type(self).__name__} is not started")

    @abstractmethod
    def _open(self) -> None:
        """Prepare the display of the group."""

    @abstractmethod
    def _add_bar(self, key: str, settings: ProgressSettings) -> None:
        """Create and display the underlying bar of ``key``."""

    @abstractmethod
    def _render_bar(self, key: str, step: int) -> None:
        """Advance the underlying bar of ``key`` by ``step`` steps."""

    @abstractmethod
    def _finish_bar(self, key: str) -> None:
        """Finalize the underlying bar of ``key``, which is still registered."""

    @abstractmethod
    def _close(self) -> None:
        """Release the resources held by the group display."""

    @property
    @abstractmethod
    def backend(self) -> ProgressBarBackend:
        """Backend implemented by this renderer."""

    @property
    def environment(self) -> RenderEnvironment:
        """Environment the group is rendered in."""
        return self._environment

    @property
    def open_keys(self) -> tuple[str, ...]:
        """Keys of the open bars, in the order they were added."""
        return tuple(self._settings_by_key)

    @property
    def is_active(self) -> bool:
        """Whether the group is currently displayed."""
        return self._is_active
