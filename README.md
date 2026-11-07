# progress-bar

## Overview

`progress_bar` renders a progress bar with whichever library is available at runtime. The same calling code works with
every backend below; when none of the optional libraries is installed, or the output is redirected, the dependency-free
plain bar is used. The package itself has no required dependencies.

| Backend | Library | Extra |
| --- | --- | --- |
| `RICH` | [rich](https://pypi.org/project/rich/) | `rich` |
| `TQDM` | [tqdm](https://pypi.org/project/tqdm/) | `tqdm` |
| `ALIVE_PROGRESS` | [alive-progress](https://pypi.org/project/alive-progress/) | `alive-progress` |
| `PROGRESSBAR2` | [progressbar2](https://pypi.org/project/progressbar2/) | `progressbar2` |
| `PLAIN` | None (text bar) | |
| `SILENT` | None (no output) | |

Automatic selection tries the optional backends in the order above; see `BackendResolver.resolve`.

## Installation

```bash
pip install -e .            # built-in plain backend only
pip install -e ".[rich]"    # one optional backend
pip install -e ".[all]"     # every optional backend
```

## Usage

Iterate over a collection and let the backend be chosen automatically:

```python
from progress_bar import ProgressBarReporter

for item in ProgressBarReporter(description="Loading").report(range(100)):
    handle(item)
```

Report steps manually when the work is not a simple loop:

```python
with ProgressBarReporter(total=100, description="Copying", unit="file") as reporter:
    for chunk in chunks:
        copy(chunk)
        reporter.advance(len(chunk))
```

Pin a backend, or turn the display off entirely:

```python
from progress_bar import ProgressBarBackend, ProgressBarReporter

reporter = ProgressBarReporter(total=10, backend=ProgressBarBackend.RICH)
quiet = ProgressBarReporter(total=10, is_enabled=False)
```

Show several bars at once, advanced from any thread, with `ProgressBarGroup`:

```python
from progress_bar import ProgressBarGroup

with ProgressBarGroup() as group:
    for scene in group.report(scenes, description="Scenes"):
        bar = group.add(total=len(scene.cameras), description=str(scene), is_leave_visible=False)
        ...
```

Worker processes join the same display through the picklable `group.remote()` proxy, passed when the process is created
and preferably with the `spawn` or `forkserver` start method (see
[src/progress_bar/group/remote/](src/progress_bar/group/remote/README.md)), and `group.snapshot()` reads how far every
open bar is, for example to report progress from a server with `ProgressBarGroup(is_enabled=False)`.

[examples/showcase.py](examples/showcase.py) runs the same workload through every installed backend.
