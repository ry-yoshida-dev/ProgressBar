# progressbar2

## Overview

Renders with [progressbar2](https://pypi.org/project/progressbar2/), which
displays the elapsed time and an estimated time of arrival. Its bar is updated
with absolute values, so the renderer forwards the accumulated step count, and an
unknown total is expressed as `progressbar.UnknownLength`.

The importable module is named `progressbar` while the distribution is named
`progressbar2`.

Install with `pip install ".[progressbar2]"`.

## Components

| Component | Responsibility |
| --- | --- |
| [renderer.py](renderer.py) | `ProgressBar2Renderer`, driving a `progressbar.ProgressBar` through the renderer lifecycle. |
