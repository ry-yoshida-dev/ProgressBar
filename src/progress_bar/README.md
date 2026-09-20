# progress_bar

## Overview

Runtime-switchable progress bars. `ProgressBarReporter` is the entry point: it
resolves a backend with `BackendResolver`, builds the matching renderer with
`RendererFactory`, and exposes a context manager plus an iterator wrapper.
Every backend implements the `ProgressRenderer` interface, so calling code
never depends on the library that ends up drawing the bar.

## Components

| Component | Responsibility |
| --- | --- |
| [backend.py](backend.py) | `ProgressBarBackend` enum with the module and distribution name of each backend. |
| [settings.py](settings.py) | `ProgressSettings`, the backend-independent description of a task. |
| [environment.py](environment.py) | `RenderEnvironment`, terminal capabilities of the output stream. |
| [renderer.py](renderer.py) | `ProgressRenderer`, the abstract lifecycle of a single bar shared by every backend. |
| [resolver.py](resolver.py) | `BackendResolver`, which picks an installed backend suited to the environment. |
| [factory.py](factory.py) | `RendererFactory`, which imports and instantiates the renderer of a backend. |
| [reporter.py](reporter.py) | `ProgressBarReporter`, the public facade used by application code. |
| [backends/](backends/) | One sub-package per rendering technique, each adapting a library to `ProgressRenderer`. |
| [py.typed](py.typed) | Marker declaring the package as typed for static analysers. |

## Examples

```python
from progress_bar import ProgressBarReporter

with ProgressBarReporter(total=3, description="Loading") as reporter:
    for _ in range(3):
        reporter.advance()
```
