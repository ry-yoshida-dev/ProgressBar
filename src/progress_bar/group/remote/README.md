# remote

## Overview

Bars of worker processes, rendered by the `ProgressBarGroup` of their parent through the picklable proxy returned by
`ProgressBarGroup.remote()`. Hand the proxy over when the process is created, for example through the `initializer` and
`initargs` of `ProcessPoolExecutor`.

## Components

| Component | Responsibility |
| --- | --- |
| [group.py](group.py) | `RemoteProgressBarGroup`, the worker-side proxy adding bars to the parent's group. |
| [bar.py](bar.py) | `RemoteProgressBar`, a bar coalescing its steps into events sent to the parent. |
| [listener.py](listener.py) | `RemoteEventListener`, the parent-side thread applying the events to the group. |
| [bar_opened.py](bar_opened.py) | `RemoteBarOpened`, the event announcing a new bar. |
| [bar_advanced.py](bar_advanced.py) | `RemoteBarAdvanced`, the event carrying completed steps. |
| [bar_finished.py](bar_finished.py) | `RemoteBarFinished`, the event announcing a finished bar. |
| [event.py](event.py) | `RemoteBarEvent`, the union of the three events. |

## Examples

```python
from concurrent.futures import ProcessPoolExecutor

from progress_bar import ProgressBarGroup, RemoteProgressBarGroup

worker_group: RemoteProgressBarGroup | None = None


def initialize(group: RemoteProgressBarGroup) -> None:
    global worker_group
    worker_group = group


def work(name: str) -> None:
    assert worker_group is not None
    for _ in worker_group.report(range(100), description=name):
        ...


with ProgressBarGroup() as group:
    with ProcessPoolExecutor(
        initializer=initialize, initargs=(group.remote(),)
    ) as pool:
        for _ in group.report(
            pool.map(work, ["a", "b", "c"]), total=3, description="Jobs"
        ):
            pass
```
