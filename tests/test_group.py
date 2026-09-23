"""Tests for the group of concurrent progress bars."""

from __future__ import annotations

import threading
from contextlib import closing

import pytest

from progress_bar import (
    GroupRendererFactory,
    ProgressBarBackend,
    ProgressBarGroup,
    RenderEnvironment,
)
from tests.terminal_stream_stub import TerminalStreamStub


class TestProgressBarGroup:
    """Behaviour of :class:`ProgressBarGroup` and the bars it hands out."""

    def _build(
        self,
        backend: ProgressBarBackend = ProgressBarBackend.SILENT,
        stream: TerminalStreamStub | None = None,
    ) -> ProgressBarGroup:
        return ProgressBarGroup(
            backend=backend,
            environment=RenderEnvironment(
                TerminalStreamStub() if stream is None else stream
            ),
        )

    def test_bars_count_their_own_steps(self) -> None:
        with self._build() as group:
            first = group.add(total=3)
            second = group.add(total=5)
            first.advance(2)
            second.advance(4)
            assert first.completed == 2
            assert second.completed == 4
            first.finish()
            second.finish()
        assert not group.is_active

    def test_adding_a_bar_requires_a_started_group(self) -> None:
        group = self._build()
        with pytest.raises(RuntimeError):
            group.add(total=1)

    def test_starting_twice_is_rejected(self) -> None:
        with self._build() as group, pytest.raises(RuntimeError):
            group.start()

    def test_finished_bar_rejects_new_steps(self) -> None:
        with self._build() as group:
            bar = group.add(total=2)
            bar.finish()
            with pytest.raises(RuntimeError):
                bar.advance()

    def test_negative_step_is_rejected(self) -> None:
        with self._build() as group:
            bar = group.add(total=2)
            with pytest.raises(ValueError):
                bar.advance(-1)

    def test_finishing_a_bar_twice_is_ignored(self) -> None:
        with self._build() as group:
            bar = group.add(total=1)
            bar.finish()
            bar.finish()
            assert not bar.is_active

    def test_bar_used_as_a_context_manager_is_finished(self) -> None:
        with self._build() as group:
            with group.add(total=2) as bar:
                bar.advance(2)
            assert not bar.is_active

    def test_report_infers_the_total_and_finishes_the_bar(self) -> None:
        stream = TerminalStreamStub(is_terminal=False)
        with self._build(ProgressBarBackend.PLAIN, stream) as group:
            items = list(group.report([1, 2, 3], description="items"))
        assert items == [1, 2, 3]
        assert "items: [" in stream.getvalue()
        assert "(3/3)" in stream.getvalue()

    def test_report_of_a_bar_finishes_it_when_closed_early(self) -> None:
        with self._build() as group:
            bar = group.add(total=10)
            with closing(bar.report(range(10))) as items:
                for item in items:
                    if item == 2:
                        break
            assert bar.completed == 2
            assert not bar.is_active

    def test_bars_can_be_advanced_from_several_threads(self) -> None:
        step_count = 500
        with self._build() as group:
            bars = [group.add(total=step_count) for _ in range(4)]

            def advance_all(index: int) -> None:
                for _ in range(step_count):
                    bars[index].advance()

            threads = [
                threading.Thread(target=advance_all, args=(index,))
                for index in range(len(bars))
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            assert [bar.completed for bar in bars] == [step_count] * len(bars)

    def test_finishing_the_group_finishes_every_open_bar(self) -> None:
        stream = TerminalStreamStub(is_terminal=False)
        with self._build(ProgressBarBackend.PLAIN, stream) as group:
            bar = group.add(total=4, description="left open")
            bar.advance(3)
        assert "left open: [" in stream.getvalue()
        assert "(3/4)" in stream.getvalue()

    def test_steps_of_a_bar_outliving_the_group_are_ignored(self) -> None:
        with self._build() as group:
            bar = group.add(total=4)
        bar.advance()
        assert bar.completed == 1

    def test_disabled_group_is_silent(self) -> None:
        stream = TerminalStreamStub()
        group = ProgressBarGroup(
            backend=ProgressBarBackend.PLAIN,
            is_enabled=False,
            environment=RenderEnvironment(stream),
        )
        with group:
            group.add(total=2, description="hidden").advance(2)
            assert not group.remote().is_enabled
        assert group.backend is ProgressBarBackend.SILENT
        assert stream.getvalue() == ""

    def test_backend_without_group_support_is_replaced(self) -> None:
        with pytest.warns(UserWarning):
            group = self._build(ProgressBarBackend.ALIVE_PROGRESS)
        assert group.backend.is_group_supported

    def test_factory_rejects_a_backend_without_group_support(self) -> None:
        factory = GroupRendererFactory(RenderEnvironment(TerminalStreamStub()))
        with pytest.raises(ValueError):
            factory.create(ProgressBarBackend.ALIVE_PROGRESS)

    def test_report_displays_its_bar_before_iteration_starts(self) -> None:
        stream = TerminalStreamStub()
        with self._build(ProgressBarBackend.PLAIN, stream) as group:
            items = group.report([1, 2], description="first")
            group.add(total=1, description="second").finish()
            rendered = stream.getvalue()
            assert list(items) == [1, 2]
        assert 0 <= rendered.index("first: [") < rendered.index("second: [")
