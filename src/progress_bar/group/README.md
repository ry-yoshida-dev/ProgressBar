# group

## Overview

Bars that run side by side. `ProgressBarGroup` draws them through one backend and can be used from any thread, and
`remote()` extends it to worker processes; code typed against `ProgressBarSource` and `ProgressTask` runs unchanged in
the parent and in a worker.

## Components

| Component | Responsibility |
| --- | --- |
| [group.py](group.py) | `ProgressBarGroup`, the public facade for concurrent bars, thread-safe and extensible to worker processes. |
| [bar.py](bar.py) | `GroupedProgressBar`, the handle of one bar of a group. |
| [source.py](source.py) | `ProgressBarSource`, the protocol of an object displaying new bars, local or remote. |
| [task.py](task.py) | `ProgressTask`, the protocol of one running bar, with iteration and context management built on it. |
| [snapshot.py](snapshot.py) | `ProgressBarSnapshot`, how far one open bar is at one moment, read by `ProgressBarGroup.snapshot()`. |
| [renderer.py](renderer.py) | `ProgressGroupRenderer`, the abstract lifecycle of a group shared by the backends that support it. |
| [factory.py](factory.py) | `GroupRendererFactory`, which imports and instantiates the group renderer of a backend. |
| [remote/](remote/README.md) | Bars of worker processes, forwarded through a queue to the group of their parent. |

## Examples

```python
from progress_bar import ProgressBarGroup

with ProgressBarGroup() as group:
    for scene in group.report(["a", "b"], description="Scenes"):
        with group.add(total=10, description=scene, is_leave_visible=False) as bar:
            bar.advance(10)
```
