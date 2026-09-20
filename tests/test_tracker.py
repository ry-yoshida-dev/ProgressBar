"""Tests for the high level tracker."""

from __future__ import annotations

import pytest

from progress_bar import (
    ProgressBarBackend,
    ProgressSettings,
    ProgressTracker,
    RenderEnvironment,
    resolver,
)
from tests.missing_package_stub import MissingPackageStub
from tests.terminal_stream_stub import TerminalStreamStub


class TestProgressTracker:
    """Behaviour of :class:`ProgressTracker`."""

    def _build(self, total: int | None = None) -> ProgressTracker:
        return ProgressTracker(
            total=total,
            backend=ProgressBarBackend.SILENT,
            environment=RenderEnvironment(TerminalStreamStub()),
        )

    def test_context_manager_counts_every_step(self) -> None:
        tracker = self._build(total=3)
        with tracker:
            for _ in range(3):
                tracker.advance()
            assert tracker.completed == 3
        assert not tracker.is_active

    def test_track_infers_the_total_from_a_sized_iterable(self) -> None:
        tracker = self._build()
        assert list(tracker.track([1, 2, 3])) == [1, 2, 3]
        assert tracker.settings.total == 3

    def test_track_of_an_empty_iterable_reports_an_empty_task(self) -> None:
        tracker = self._build()
        assert list(tracker.track([])) == []
        assert tracker.settings.total == 0

    def test_track_supports_an_iterator_without_length(self) -> None:
        tracker = self._build()
        assert list(tracker.track(iter([1, 2]))) == [1, 2]
        assert tracker.settings.total is None

    def test_disabled_tracker_uses_the_silent_backend(self) -> None:
        tracker = ProgressTracker(total=2, is_enabled=False)
        assert tracker.backend is ProgressBarBackend.SILENT

    def test_backend_cannot_be_switched_while_running(self) -> None:
        tracker = self._build(total=2)
        with tracker, pytest.raises(RuntimeError):
            tracker.switch_to(ProgressBarBackend.PLAIN)

    def test_switch_falls_back_when_the_package_is_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(resolver, "find_spec", MissingPackageStub())
        tracker = self._build(total=2)
        assert tracker.switch_to(ProgressBarBackend.TQDM) is ProgressBarBackend.PLAIN

    def test_switch_honours_an_installed_backend(self) -> None:
        tracker = self._build(total=2)
        assert tracker.switch_to(ProgressBarBackend.PLAIN) is ProgressBarBackend.PLAIN

    def test_advance_before_start_is_rejected(self) -> None:
        tracker = self._build(total=2)
        with pytest.raises(RuntimeError):
            tracker.advance()

    def test_start_twice_is_rejected(self) -> None:
        tracker = self._build(total=2)
        with tracker, pytest.raises(RuntimeError):
            tracker.start()

    def test_negative_step_is_rejected(self) -> None:
        tracker = self._build(total=2)
        with tracker, pytest.raises(ValueError):
            tracker.advance(-1)

    def test_zero_step_is_accepted_as_a_no_op(self) -> None:
        tracker = self._build(total=2)
        with tracker:
            tracker.advance(0)
            assert tracker.completed == 0

    def test_from_settings_keeps_every_field(self) -> None:
        settings = ProgressSettings(total=5, description="load", unit="file")
        tracker = ProgressTracker.from_settings(
            settings,
            backend=ProgressBarBackend.SILENT,
            environment=RenderEnvironment(TerminalStreamStub()),
        )
        assert tracker.settings == settings

    def test_negative_total_is_rejected(self) -> None:
        with pytest.raises(ValueError):
            ProgressSettings(total=-1)
