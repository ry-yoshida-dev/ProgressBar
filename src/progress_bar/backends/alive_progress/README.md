# alive_progress

## Overview

Renders with [alive-progress](https://pypi.org/project/alive-progress/). Its bar owns the terminal, so it cannot render a
`ProgressBarGroup`. Install with `pip install ".[alive-progress]"`.

## Components

| Component | Responsibility |
| --- | --- |
| [renderer.py](renderer.py) | `AliveProgressRenderer`, keeping the `alive_bar` context open for the task. |
| [bar_handle.py](bar_handle.py) | `AliveBarHandle`, the protocol typing the handle `alive_bar` yields. |
