# progressbar2

## Overview

Renders with [progressbar2](https://pypi.org/project/progressbar2/). Install with `pip install ".[progressbar2]"`.

## Components

| Component | Responsibility |
| --- | --- |
| [renderer.py](renderer.py) | `ProgressBar2Renderer`, driving a `progressbar.ProgressBar` through the renderer lifecycle. |
| [group_renderer.py](group_renderer.py) | `ProgressBar2GroupRenderer`, drawing the bars of a group through one `progressbar.MultiBar`. |
