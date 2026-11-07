# tqdm

## Overview

Renders with [tqdm](https://pypi.org/project/tqdm/). Install with `pip install ".[tqdm]"`.

## Components

| Component | Responsibility |
| --- | --- |
| [renderer.py](renderer.py) | `TqdmRenderer`, driving a `tqdm` instance through the renderer lifecycle. |
| [group_renderer.py](group_renderer.py) | `TqdmGroupRenderer`, placing every bar of a group on a `tqdm` line of its own. |
