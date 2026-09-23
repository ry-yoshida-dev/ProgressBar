# group

## Overview

Bars that run side by side. `ProgressBarGroup` resolves a backend with
`BackendResolver.resolve_group`, builds one `ProgressGroupRenderer` with
`GroupRendererFactory`, and hands out a `GroupedProgressBar` per bar. It
serializes every call to the renderer, so bars can be added, advanced and
finished from any thread, and `remote()` extends the group to worker processes
through `remote/`.

Calling code depends only on two protocols: `ProgressBarSource`, implemented by
the local group and its remote proxy, and `ProgressTask`, implemented by the
bars they hand out. The same code therefore runs in the parent process and in a
worker.

## Components

| Component | Responsibility |
| --- | --- |
| [group.py](group.py) | `ProgressBarGroup`, the public facade for concurrent bars, thread-safe and extensible to worker processes. |
| [bar.py](bar.py) | `GroupedProgressBar`, the handle of one bar of a group. |
| [source.py](source.py) | `ProgressBarSource`, the protocol of an object displaying new bars, local or remote. |
| [task.py](task.py) | `ProgressTask`, the protocol of one running bar, with iteration and context management built on it. |
| [renderer.py](renderer.py) | `ProgressGroupRenderer`, the abstract lifecycle of a group shared by the backends that support it. |
| [factory.py](factory.py) | `GroupRendererFactory`, which imports and instantiates the group renderer of a backend. |
| [remote/](remote/) | Bars of worker processes, forwarded through a queue to the group of their parent. |

## Examples

```python
from progress_bar import ProgressBarGroup

with ProgressBarGroup() as group:
    for scene in group.report(["a", "b"], description="Scenes"):
        with group.add(total=10, description=scene, is_leave_visible=False) as bar:
            bar.advance(10)
```
