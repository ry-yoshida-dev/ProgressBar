# alive_progress

## Overview

Renders with [alive-progress](https://pypi.org/project/alive-progress/), whose
animated bar keeps moving while a step is being processed. Its API is a context
manager yielding a callable, so the renderer keeps that context open in an
`ExitStack` for the lifetime of the task.

The library does not annotate the yielded callable, which is why `AliveBarHandle`
pins down its call signature for static analysis.

Its bar owns the terminal until it finishes, so it cannot render a
`ProgressBarGroup`; a group that asks for it is rendered by another backend.

Install with `pip install ".[alive-progress]"`.

## Components

| Component | Responsibility |
| --- | --- |
| [renderer.py](renderer.py) | `AliveProgressRenderer`, keeping the `alive_bar` context open for the task. |
| [bar_handle.py](bar_handle.py) | `AliveBarHandle`, the protocol typing the handle `alive_bar` yields. |
