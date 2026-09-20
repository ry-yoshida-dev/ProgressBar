"""Tests for the adapters wrapping an optional third-party library."""

from __future__ import annotations

from typing import Final

import pytest

from progress_bar import (
    BackendResolver,
    ProgressBarBackend,
    ProgressSettings,
    RenderEnvironment,
    ReporterFactory,
)
from tests.terminal_stream_stub import TerminalStreamStub


class TestThirdPartyAdapters:
    """Lifecycle of every adapter that renders with an optional package."""

    THIRD_PARTY_BACKENDS: Final[tuple[ProgressBarBackend, ...]] = (
        ProgressBarBackend.TQDM,
        ProgressBarBackend.PROGRESSBAR2,
        ProgressBarBackend.ALIVE_PROGRESS,
        ProgressBarBackend.RICH,
    )

    def _create_stream(self, backend: ProgressBarBackend) -> TerminalStreamStub:
        if not BackendResolver().is_installed(backend):
            pytest.skip(f"{backend.distribution_name} is not installed")
        return TerminalStreamStub()

    @pytest.mark.parametrize("backend", THIRD_PARTY_BACKENDS)
    def test_lifecycle_counts_every_step_and_writes_to_the_stream(
        self, backend: ProgressBarBackend
    ) -> None:
        stream = self._create_stream(backend)
        reporter = ReporterFactory(RenderEnvironment(stream)).create(
            backend, ProgressSettings(total=4, description="load")
        )
        with reporter:
            assert reporter.is_active
            for _ in range(4):
                reporter.advance()
        assert reporter.backend is backend
        assert reporter.completed == 4
        assert not reporter.is_active
        assert stream.getvalue() != ""

    @pytest.mark.parametrize("backend", THIRD_PARTY_BACKENDS)
    def test_unknown_total_is_supported(self, backend: ProgressBarBackend) -> None:
        stream = self._create_stream(backend)
        reporter = ReporterFactory(RenderEnvironment(stream)).create(
            backend, ProgressSettings(description="stream")
        )
        with reporter:
            reporter.advance(3)
        assert reporter.completed == 3

    @pytest.mark.parametrize("backend", THIRD_PARTY_BACKENDS)
    def test_empty_task_is_supported(self, backend: ProgressBarBackend) -> None:
        stream = self._create_stream(backend)
        reporter = ReporterFactory(RenderEnvironment(stream)).create(
            backend, ProgressSettings(total=0, description="empty")
        )
        with reporter:
            pass
        assert reporter.completed == 0

    @pytest.mark.parametrize("backend", THIRD_PARTY_BACKENDS)
    def test_transient_bar_is_closed_without_error(
        self, backend: ProgressBarBackend
    ) -> None:
        stream = self._create_stream(backend)
        reporter = ReporterFactory(RenderEnvironment(stream)).create(
            backend, ProgressSettings(total=2, is_leave_visible=False)
        )
        with reporter:
            reporter.advance(2)
        assert not reporter.is_active
