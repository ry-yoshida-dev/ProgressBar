"""Runnable demonstration of the available progress bar backends."""

from __future__ import annotations

import time

from progress_bar import BackendResolver, ProgressBarBackend, ProgressTracker


class BackendShowcase:
    """Runs the same workload once per backend.

    Parameters
    ----------
    steps
        Number of simulated work items.
    step_duration
        Seconds spent on a single work item.
    """

    def __init__(self, steps: int = 40, step_duration: float = 0.03) -> None:
        if steps <= 0:
            raise ValueError(f"steps must be positive, got {steps}")
        self._steps = steps
        self._step_duration = step_duration
        self._resolver = BackendResolver()

    def run(self) -> None:
        """Render the workload with the automatic choice and every backend."""
        print(f"installed backends: {self._installed_names()}")
        print(f"automatic choice: {self._resolver.resolve().value}\n")
        self._run_automatic()
        for backend in self._resolver.installed_backends():
            self._run_backend(backend)

    def _installed_names(self) -> str:
        return ", ".join(
            backend.value for backend in self._resolver.installed_backends()
        )

    def _run_automatic(self) -> None:
        print("[auto] iterating over a list")
        tracker = ProgressTracker(description="auto")
        for _ in tracker.track(range(self._steps)):
            time.sleep(self._step_duration)

    def _run_backend(self, backend: ProgressBarBackend) -> None:
        print(f"[{backend.value}] manual stepping")
        with ProgressTracker(
            total=self._steps, description=backend.value, backend=backend
        ) as tracker:
            for _ in range(self._steps):
                time.sleep(self._step_duration)
                tracker.advance()


if __name__ == "__main__":
    BackendShowcase().run()
