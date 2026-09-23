"""Tests for the bars of worker processes rendered by a parent group."""

from __future__ import annotations

import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from multiprocessing.queues import Queue

from progress_bar import (
    ProgressBarBackend,
    ProgressBarGroup,
    ProgressSettings,
    RemoteProgressBar,
    RemoteProgressBarGroup,
    RenderEnvironment,
)
from progress_bar.group.remote import (
    RemoteBarAdvanced,
    RemoteBarEvent,
    RemoteBarFinished,
    RemoteBarOpened,
)
from tests.remote_worker_stub import RemoteWorkerStub
from tests.terminal_stream_stub import TerminalStreamStub


class TestRemoteProgressBar:
    """Behaviour of the worker-side bar and group."""

    def _drain(self, queue: Queue[RemoteBarEvent | None]) -> list[RemoteBarEvent]:
        events: list[RemoteBarEvent] = []
        while True:
            event = queue.get(timeout=5)
            if event is None:
                return events
            events.append(event)

    def test_steps_are_coalesced_until_the_total_is_reached(self) -> None:
        queue: Queue[RemoteBarEvent | None] = multiprocessing.get_context().Queue()
        bar = RemoteProgressBarGroup(queue).add(total=5, description="load")
        for _ in range(5):
            bar.advance()
        bar.finish()
        queue.put(None)
        events = self._drain(queue)
        assert isinstance(events[0], RemoteBarOpened)
        assert isinstance(events[-1], RemoteBarFinished)
        advanced = [event for event in events if isinstance(event, RemoteBarAdvanced)]
        assert sum(event.step for event in advanced) == 5
        assert len(advanced) < 5
        queue.close()

    def test_bar_without_queue_only_counts(self) -> None:
        bar = RemoteProgressBar(None, ProgressSettings(total=2))
        bar.advance(2)
        bar.finish()
        assert bar.completed == 2
        assert not bar.is_active

    def test_worker_bars_are_rendered_by_the_parent_group(self) -> None:
        stream = TerminalStreamStub(is_terminal=False)
        context = multiprocessing.get_context("spawn")
        group = ProgressBarGroup(
            backend=ProgressBarBackend.PLAIN,
            environment=RenderEnvironment(stream),
            context=context,
        )
        with group:
            remote = group.remote()
            with ProcessPoolExecutor(
                max_workers=2,
                mp_context=context,
                initializer=RemoteWorkerStub.initialize,
                initargs=(remote,),
            ) as executor:
                futures = [
                    executor.submit(RemoteWorkerStub.run, f"worker {index}", 20, True)
                    for index in range(3)
                ]
                results = [future.result() for future in futures]
        assert results == [20, 20, 20]
        rendered = stream.getvalue()
        for index in range(3):
            assert f"worker {index}: [{'#' * 30}] 100.0% (20/20)" in rendered

    def test_remote_of_a_remote_group_is_the_same_proxy(self) -> None:
        remote = RemoteProgressBarGroup(None)
        assert remote.remote() is remote
