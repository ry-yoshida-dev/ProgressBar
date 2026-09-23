# progress-bar

## Overview

`progress_bar` renders a progress bar with whichever library happens to be
available at runtime. The same calling code works with
[tqdm](https://pypi.org/project/tqdm/),
[progressbar2](https://pypi.org/project/progressbar2/),
[alive-progress](https://pypi.org/project/alive-progress/) and
[rich](https://pypi.org/project/rich/); when none of them is installed, or the
output is redirected to a file, a dependency-free text bar is used instead.

The package itself has no required dependencies, so it can be used in a project
that does not want to commit to a single progress bar library.

## Installation

```bash
pip install -e .            # built-in plain backend only
pip install -e ".[rich]"    # one optional backend
pip install -e ".[all]"     # every optional backend
pip install -e ".[dev]"     # backends plus mypy, pytest and ruff
```

## Usage

Iterate over a collection and let the backend be chosen automatically:

```python
from progress_bar import ProgressBarReporter

for item in ProgressBarReporter(description="Loading").report(range(100)):
    handle(item)
```

`report` returns a generator, so a loop that stops early leaves the bar open
until the generator is closed. Wrap it in `contextlib.closing` when a
reference to it outlives the loop:

```python
from contextlib import closing

with closing(ProgressBarReporter(total=100).report(range(100))) as items:
    for item in items:
        if is_enough(item):
            break
```

Report steps manually when the work is not a simple loop:

```python
with ProgressBarReporter(total=100, description="Copying", unit="file") as reporter:
    for chunk in chunks:
        copy(chunk)
        reporter.advance(len(chunk))
```

A total of zero describes an empty task and renders a completed bar, and a
step of zero leaves the bar untouched, so neither an empty collection nor an
empty batch needs a special case at the call site.

Pin a backend, or turn the display off entirely:

```python
from progress_bar import ProgressBarBackend, ProgressBarReporter

reporter = ProgressBarReporter(total=10, backend=ProgressBarBackend.RICH)
quiet = ProgressBarReporter(total=10, is_enabled=False)
```

Inspect and change the choice at runtime:

```python
reporter = ProgressBarReporter(total=10)
print(reporter.backend)  # the backend that will be used
print(reporter.installed_backends)  # everything importable right now
reporter.switch_to(ProgressBarBackend.TQDM)
```

`examples/showcase.py` runs the same workload through every installed backend.

## Concurrent Bars

`ProgressBarGroup` displays several bars at once, each on a line of its own,
drawn by one backend so they never overwrite each other. Bars can be added and
finished at any time while the group is open, and advanced from any thread:

```python
from progress_bar import ProgressBarGroup

with ProgressBarGroup() as group:
    for scene in group.report(scenes, description="Scenes", unit="scene"):
        bars = [
            group.add(
                total=len(camera),
                description=f"{scene} [{camera}]",
                is_leave_visible=False,
            )
            for camera in scene.cameras
        ]
        ...
```

`group.add()` returns a bar that is already displayed; `advance()`, `finish()`,
`report()` and the context manager work as on `ProgressBarReporter`. A bar with
`is_leave_visible=False` disappears when it finishes, and finishing the group
finishes every bar still open.

Worker processes add bars to the same display through `group.remote()`, a
picklable proxy that forwards their progress over a queue. The queue only
reaches a child through inheritance, so pass the proxy when the process is
created, for example through `ProcessPoolExecutor(initializer=...,
initargs=(group.remote(),))`; see [src/progress_bar/group/remote/](src/progress_bar/group/remote/README.md).
Code that only adds bars can be typed against `ProgressBarSource` and run
unchanged in the parent and in a worker. Prefer the `spawn` or `forkserver`
start method, since the group runs a listener thread and `fork` copies a
multi-threaded process.

Every backend except `alive_progress`, whose bar owns the terminal, can render
a group. A group that asks for `alive_progress` warns and uses the automatic
choice instead.

## Backend Selection

`BackendResolver` applies the following rules, in order:

1. A backend requested by the caller wins if its package is installed.
2. A redirected or non-interactive stream falls back to the plain backend,
   which prints one line per 10% instead of redrawing.
3. Otherwise the first installed backend of `rich`, `tqdm`, `alive_progress`,
   `progressbar2` is used.
4. The plain backend is the last resort and never fails.

A missing package therefore degrades the display instead of raising. Use
`BackendResolver.require()` when a specific backend is mandatory.
`BackendResolver.resolve_group()` applies the same rules to a group, skipping
the backends that cannot display several bars at once.

## Development

```bash
pytest
mypy
ruff check .
ruff format --check .
```

GitHub Actions runs the same checks on Python 3.12 and 3.13, plus the suite in
an environment without any optional backend installed.
