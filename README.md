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

for item in ProgressBarReporter(description="Loading").track(range(100)):
    handle(item)
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

## Development

```bash
pytest
mypy
ruff check .
ruff format --check .
```

GitHub Actions runs the same checks on Python 3.12 and 3.13, plus the suite in
an environment without any optional backend installed.
