# alive_progress

## Overview

Renders with [alive-progress](https://pypi.org/project/alive-progress/), whose
animated bar keeps moving while a step is being processed. Its API is a context
manager yielding a callable, so the adapter keeps that context open in an
`ExitStack` for the lifetime of the task.

The library does not annotate the yielded callable, which is why `AliveBarHandle`
pins down its call signature for static analysis.

Install with `pip install ".[alive-progress]"`.

## Components

| Component | Responsibility |
| --- | --- |
| [adapter.py](adapter.py) | `AliveProgressAdapter`, keeping the `alive_bar` context open for the task. |
| [bar_handle.py](bar_handle.py) | `AliveBarHandle`, the protocol typing the handle `alive_bar` yields. |
