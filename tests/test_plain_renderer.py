"""Tests for the dependency-free renderer."""

from __future__ import annotations

from progress_bar import ProgressBarBackend, ProgressSettings, RenderEnvironment
from progress_bar.backends.plain import PlainRenderer
from tests.terminal_stream_stub import TerminalStreamStub


class TestPlainRenderer:
    """Behaviour of :class:`PlainRenderer`."""

    def test_terminal_output_is_redrawn_in_place(self) -> None:
        stream = TerminalStreamStub()
        renderer = PlainRenderer(
            ProgressSettings(total=2, description="load"),
            RenderEnvironment(stream),
        )
        with renderer:
            renderer.advance()
            renderer.advance()
        rendered = stream.getvalue()
        assert renderer.backend is ProgressBarBackend.PLAIN
        assert "load: [" in rendered
        assert "100.0% (2/2)" in rendered
        assert "\r" in rendered

    def test_redirected_output_is_written_per_milestone(self) -> None:
        stream = TerminalStreamStub(is_terminal=False)
        renderer = PlainRenderer(ProgressSettings(total=100), RenderEnvironment(stream))
        with renderer:
            for _ in range(100):
                renderer.advance()
        lines = [line for line in stream.getvalue().splitlines() if line]
        assert len(lines) == 10
        assert "\r" not in stream.getvalue()

    def test_redirected_output_does_not_repeat_the_final_milestone(self) -> None:
        stream = TerminalStreamStub(is_terminal=False)
        renderer = PlainRenderer(ProgressSettings(total=10), RenderEnvironment(stream))
        with renderer:
            for _ in range(10):
                renderer.advance()
        lines = [line for line in stream.getvalue().splitlines() if line]
        assert lines.count(lines[-1]) == 1
        assert "100.0% (10/10)" in lines[-1]

    def test_interrupted_task_still_reports_its_final_state(self) -> None:
        stream = TerminalStreamStub(is_terminal=False)
        renderer = PlainRenderer(ProgressSettings(total=10), RenderEnvironment(stream))
        with renderer:
            renderer.advance(5)
            renderer.advance(2)
        lines = [line for line in stream.getvalue().splitlines() if line]
        assert "70.0% (7/10)" in lines[-1]

    def test_transient_bar_is_cleared_on_exit(self) -> None:
        stream = TerminalStreamStub()
        renderer = PlainRenderer(
            ProgressSettings(total=2, is_leave_visible=False),
            RenderEnvironment(stream),
        )
        with renderer:
            renderer.advance()
        assert stream.getvalue().endswith("\r")

    def test_empty_task_renders_a_complete_bar(self) -> None:
        stream = TerminalStreamStub(is_terminal=False)
        renderer = PlainRenderer(
            ProgressSettings(total=0, description="empty"),
            RenderEnvironment(stream),
        )
        with renderer:
            pass
        assert "empty: [" in stream.getvalue()
        assert "100.0% (0/0)" in stream.getvalue()

    def test_zero_step_leaves_the_bar_untouched(self) -> None:
        stream = TerminalStreamStub(is_terminal=False)
        renderer = PlainRenderer(ProgressSettings(total=10), RenderEnvironment(stream))
        with renderer:
            renderer.advance(0)
            assert renderer.completed == 0
        assert "0.0% (0/10)" in stream.getvalue()
