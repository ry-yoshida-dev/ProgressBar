# progress_bar

## Overview

Runtime-switchable progress bars. `ProgressTracker` is the entry point: it
resolves a backend with `BackendResolver`, builds the matching reporter with
`ReporterFactory`, and exposes a context manager plus an iterator wrapper.
Every backend implements the `ProgressReporter` interface, so calling code
never depends on the library that ends up rendering the bar.

## Components

| Component | Responsibility |
| --- | --- |
| [backend.py](backend.py) | `ProgressBarBackend` enum with the module and distribution name of each backend. |
| [settings.py](settings.py) | `ProgressSettings`, the backend-independent description of a task. |
| [environment.py](environment.py) | `RenderEnvironment`, terminal capabilities of the output stream. |
| [reporter.py](reporter.py) | `ProgressReporter`, the abstract lifecycle shared by every backend. |
| [resolver.py](resolver.py) | `BackendResolver`, which picks an installed backend suited to the environment. |
| [factory.py](factory.py) | `ReporterFactory`, which imports and instantiates the adapter of a backend. |
| [tracker.py](tracker.py) | `ProgressTracker`, the public facade used by application code. |
| [backends/](backends/) | One sub-package per rendering technique, each adapting a library to `ProgressReporter`. |
| [py.typed](py.typed) | Marker declaring the package as typed for static analysers. |

## Examples

```python
from progress_bar import ProgressTracker

with ProgressTracker(total=3, description="Loading") as tracker:
    for _ in range(3):
        tracker.advance()
```
