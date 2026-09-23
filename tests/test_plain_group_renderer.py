"""Tests for the dependency-free group renderer."""

from __future__ import annotations

import pytest

from progress_bar import ProgressBarBackend, ProgressSettings, RenderEnvironment
from progress_bar.backends.plain import PlainGroupRenderer
from tests.terminal_stream_stub import TerminalStreamStub


class TestPlainGroupRenderer:
    """Behaviour of :class:`PlainGroupRenderer`."""

    def test_terminal_output_redraws_every_bar_in_place(self) -> None:
        stream = TerminalStreamStub()
        renderer = PlainGroupRenderer(RenderEnvironment(stream))
        with renderer:
            renderer.add_bar("a", ProgressSettings(total=2, description="first"))
            renderer.add_bar("b", ProgressSettings(total=2, description="second"))
            renderer.advance_bar("a", 2)
            renderer.advance_bar("b", 2)
        rendered = stream.getvalue()
        assert renderer.backend is ProgressBarBackend.PLAIN
        assert "first: [" in rendered
        assert "second: [" in rendered
        assert "\x1b[2F" in rendered

    def test_terminal_keeps_only_the_bars_that_stay_visible(self) -> None:
        stream = TerminalStreamStub()
        renderer = PlainGroupRenderer(RenderEnvironment(stream))
        with renderer:
            renderer.add_bar("kept", ProgressSettings(total=1, description="kept"))
            renderer.add_bar(
                "gone",
                ProgressSettings(total=1, description="gone", is_leave_visible=False),
            )
            renderer.advance_bar("kept")
            renderer.advance_bar("gone")
            renderer.finish_bar("gone")
            renderer.finish_bar("kept")
            assert renderer.open_keys == ()
        rendered = stream.getvalue()
        assert rendered.endswith("\x1b[2Kkept: [" + "#" * 30 + "] 100.0% (1/1)\n")

    def test_redirected_output_logs_each_bar_per_milestone(self) -> None:
        stream = TerminalStreamStub(is_terminal=False)
        renderer = PlainGroupRenderer(RenderEnvironment(stream))
        with renderer:
            renderer.add_bar("a", ProgressSettings(total=10, description="a"))
            renderer.add_bar("b", ProgressSettings(total=10, description="b"))
            for _ in range(10):
                renderer.advance_bar("a")
                renderer.advance_bar("b")
        lines = [line for line in stream.getvalue().splitlines() if line]
        assert sum(line.startswith("a: ") for line in lines) == 10
        assert sum(line.startswith("b: ") for line in lines) == 10
        assert "\x1b" not in stream.getvalue()

    def test_redirected_transient_bar_writes_no_final_line(self) -> None:
        stream = TerminalStreamStub(is_terminal=False)
        renderer = PlainGroupRenderer(RenderEnvironment(stream))
        with renderer:
            renderer.add_bar(
                "a", ProgressSettings(total=10, description="a", is_leave_visible=False)
            )
            renderer.advance_bar("a", 5)
        lines = [line for line in stream.getvalue().splitlines() if line]
        assert lines == ["a: [###############---------------]  50.0% (5/10)"]

    def test_duplicate_key_is_rejected(self) -> None:
        renderer = PlainGroupRenderer(RenderEnvironment(TerminalStreamStub()))
        with renderer:
            renderer.add_bar("a", ProgressSettings())
            with pytest.raises(ValueError):
                renderer.add_bar("a", ProgressSettings())
