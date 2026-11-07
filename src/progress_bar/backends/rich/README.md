# rich

## Overview

Renders with [rich](https://pypi.org/project/rich/). Install with `pip install ".[rich]"`.

## Components

| Component | Responsibility |
| --- | --- |
| [renderer.py](renderer.py) | `RichRenderer`, driving one task of `rich.progress.Progress`. |
| [group_renderer.py](group_renderer.py) | `RichGroupRenderer`, drawing every bar of a group as a task of one `Progress`. |
