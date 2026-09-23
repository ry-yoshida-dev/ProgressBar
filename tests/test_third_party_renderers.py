"""Tests for the renderers wrapping an optional third-party library."""

from __future__ import annotations

from typing import Final

import pytest

from progress_bar import (
    BackendResolver,
    GroupRendererFactory,
    ProgressBarBackend,
    ProgressSettings,
    RenderEnvironment,
    RendererFactory,
)
from tests.terminal_stream_stub import TerminalStreamStub


class TestThirdPartyRenderers:
    """Lifecycle of every renderer that uses an optional package."""

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
        renderer = RendererFactory(RenderEnvironment(stream)).create(
            backend, ProgressSettings(total=4, description="load")
        )
        with renderer:
            assert renderer.is_active
            for _ in range(4):
                renderer.advance()
        assert renderer.backend is backend
        assert renderer.completed == 4
        assert not renderer.is_active
        assert stream.getvalue() != ""

    @pytest.mark.parametrize("backend", THIRD_PARTY_BACKENDS)
    def test_unknown_total_is_supported(self, backend: ProgressBarBackend) -> None:
        stream = self._create_stream(backend)
        renderer = RendererFactory(RenderEnvironment(stream)).create(
            backend, ProgressSettings(description="stream")
        )
        with renderer:
            renderer.advance(3)
        assert renderer.completed == 3

    @pytest.mark.parametrize("backend", THIRD_PARTY_BACKENDS)
    def test_empty_task_is_supported(self, backend: ProgressBarBackend) -> None:
        stream = self._create_stream(backend)
        renderer = RendererFactory(RenderEnvironment(stream)).create(
            backend, ProgressSettings(total=0, description="empty")
        )
        with renderer:
            pass
        assert renderer.completed == 0

    @pytest.mark.parametrize("backend", THIRD_PARTY_BACKENDS)
    def test_transient_bar_is_closed_without_error(
        self, backend: ProgressBarBackend
    ) -> None:
        stream = self._create_stream(backend)
        renderer = RendererFactory(RenderEnvironment(stream)).create(
            backend, ProgressSettings(total=2, is_leave_visible=False)
        )
        with renderer:
            renderer.advance(2)
        assert not renderer.is_active


class TestThirdPartyGroupRenderers:
    """Lifecycle of every group renderer that uses an optional package."""

    GROUP_BACKENDS: Final[tuple[ProgressBarBackend, ...]] = (
        ProgressBarBackend.TQDM,
        ProgressBarBackend.PROGRESSBAR2,
        ProgressBarBackend.RICH,
    )

    @pytest.mark.parametrize("backend", GROUP_BACKENDS)
    def test_bars_are_added_advanced_and_finished_independently(
        self, backend: ProgressBarBackend
    ) -> None:
        if not BackendResolver().is_installed(backend):
            pytest.skip(f"{backend.distribution_name} is not installed")
        stream = TerminalStreamStub()
        renderer = GroupRendererFactory(RenderEnvironment(stream)).create(backend)
        with renderer:
            renderer.add_bar("kept", ProgressSettings(total=3, description="kept"))
            renderer.add_bar(
                "gone",
                ProgressSettings(total=2, description="gone", is_leave_visible=False),
            )
            renderer.add_bar("unknown", ProgressSettings(description="unknown"))
            renderer.advance_bar("kept", 3)
            renderer.advance_bar("gone", 2)
            renderer.advance_bar("unknown", 5)
            assert renderer.completed_of("unknown") == 5
            renderer.finish_bar("gone")
            keys_after_removal: tuple[str, ...] = renderer.open_keys
            assert keys_after_removal == ("kept", "unknown")
            renderer.add_bar("next", ProgressSettings(total=1, description="next"))
        assert renderer.backend is backend
        keys_after_close: tuple[str, ...] = renderer.open_keys
        assert not renderer.is_active
        assert keys_after_close == ()
        assert "kept" in stream.getvalue()
