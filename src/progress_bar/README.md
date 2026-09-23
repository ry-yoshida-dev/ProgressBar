# progress_bar

## Overview

Runtime-switchable progress bars. `ProgressBarReporter` is the entry point for
a single bar: it resolves a backend with `BackendResolver`, builds the matching
renderer with `RendererFactory`, and exposes a context manager plus an iterator
wrapper. `ProgressBarGroup`, in `group/`, is the entry point for bars that run
side by side, from any thread or worker process. Every backend implements the
single-bar interface, and every backend but `alive_progress` the group one, so
calling code never depends on the library that ends up drawing the bars.

## Components

| Component | Responsibility |
| --- | --- |
| [backend.py](backend.py) | `ProgressBarBackend` enum with the module and distribution name of each backend. |
| [settings.py](settings.py) | `ProgressSettings`, the backend-independent description of a task. |
| [environment.py](environment.py) | `RenderEnvironment`, terminal capabilities of the output stream. |
| [renderer.py](renderer.py) | `ProgressRenderer`, the abstract lifecycle of a single bar shared by every backend. |
| [resolver.py](resolver.py) | `BackendResolver`, which picks an installed backend suited to the environment. |
| [factory.py](factory.py) | `RendererFactory`, which imports and instantiates the renderer of a backend. |
| [reporter.py](reporter.py) | `ProgressBarReporter`, the public facade for a single bar. |
| [group/](group/) | `ProgressBarGroup` and its bars, displayed together from threads or worker processes. |
| [backends/](backends/) | One sub-package per rendering technique, each adapting a library to `ProgressRenderer`. |
| [py.typed](py.typed) | Marker declaring the package as typed for static analysers. |

## Examples

```python
from progress_bar import ProgressBarGroup, ProgressBarReporter

with ProgressBarReporter(total=3, description="Loading") as reporter:
    for _ in range(3):
        reporter.advance()

with ProgressBarGroup() as group:
    for camera in group.report(["a", "b"], description="Cameras"):
        with group.add(total=10, description=camera, is_leave_visible=False) as bar:
            bar.advance(10)
```
