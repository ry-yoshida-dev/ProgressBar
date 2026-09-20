"""Tests for the high level reporter."""

from __future__ import annotations

import pytest

from progress_bar import (
    ProgressBarBackend,
    ProgressBarReporter,
    ProgressSettings,
    RenderEnvironment,
    resolver,
)
from tests.missing_package_stub import MissingPackageStub
from tests.terminal_stream_stub import TerminalStreamStub


class TestProgressBarReporter:
    """Behaviour of :class:`ProgressBarReporter`."""

    def _build(self, total: int | None = None) -> ProgressBarReporter:
        return ProgressBarReporter(
            total=total,
            backend=ProgressBarBackend.SILENT,
            environment=RenderEnvironment(TerminalStreamStub()),
        )

    def test_context_manager_counts_every_step(self) -> None:
        reporter = self._build(total=3)
        with reporter:
            for _ in range(3):
                reporter.advance()
            assert reporter.completed == 3
        assert not reporter.is_active

    def test_report_infers_the_total_from_a_sized_iterable(self) -> None:
        reporter = self._build()
        assert list(reporter.report([1, 2, 3])) == [1, 2, 3]
        assert reporter.settings.total == 3

    def test_report_of_an_empty_iterable_reports_an_empty_task(self) -> None:
        reporter = self._build()
        empty_items: list[int] = []
        assert list(reporter.report(empty_items)) == []
        assert reporter.settings.total == 0

    def test_report_supports_an_iterator_without_length(self) -> None:
        reporter = self._build()
        assert list(reporter.report(iter([1, 2]))) == [1, 2]
        assert reporter.settings.total is None

    def test_disabled_reporter_uses_the_silent_backend(self) -> None:
        reporter = ProgressBarReporter(total=2, is_enabled=False)
        assert reporter.backend is ProgressBarBackend.SILENT

    def test_backend_cannot_be_switched_while_running(self) -> None:
        reporter = self._build(total=2)
        with reporter, pytest.raises(RuntimeError):
            reporter.switch_to(ProgressBarBackend.PLAIN)

    def test_switch_falls_back_when_the_package_is_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(resolver, "find_spec", MissingPackageStub())
        reporter = self._build(total=2)
        assert reporter.switch_to(ProgressBarBackend.TQDM) is ProgressBarBackend.PLAIN

    def test_switch_honours_an_installed_backend(self) -> None:
        reporter = self._build(total=2)
        assert reporter.switch_to(ProgressBarBackend.PLAIN) is ProgressBarBackend.PLAIN

    def test_advance_before_start_is_rejected(self) -> None:
        reporter = self._build(total=2)
        with pytest.raises(RuntimeError):
            reporter.advance()

    def test_start_twice_is_rejected(self) -> None:
        reporter = self._build(total=2)
        with reporter, pytest.raises(RuntimeError):
            reporter.start()

    def test_negative_step_is_rejected(self) -> None:
        reporter = self._build(total=2)
        with reporter, pytest.raises(ValueError):
            reporter.advance(-1)

    def test_zero_step_is_accepted_as_a_no_op(self) -> None:
        reporter = self._build(total=2)
        with reporter:
            reporter.advance(0)
            assert reporter.completed == 0

    def test_from_settings_keeps_every_field(self) -> None:
        settings = ProgressSettings(total=5, description="load", unit="file")
        reporter = ProgressBarReporter.from_settings(
            settings,
            backend=ProgressBarBackend.SILENT,
            environment=RenderEnvironment(TerminalStreamStub()),
        )
        assert reporter.settings == settings

    def test_negative_total_is_rejected(self) -> None:
        with pytest.raises(ValueError):
            ProgressSettings(total=-1)
