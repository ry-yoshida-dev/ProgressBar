# tqdm

## Overview

Renders with [tqdm](https://pypi.org/project/tqdm/), the most widespread
progress bar library. `tqdm.auto` is used, so the notebook widget is picked up
automatically when the code runs inside Jupyter. An unknown total is supported
natively and falls back to a running counter.

In a group every bar gets its own `position`, the lowest line no other bar
occupies. `tqdm` writes the final state of a bar it leaves on screen at the
cursor rather than on the bar's line, so a finished bar that stays visible is
cleared and its final line is written above the running bars with `tqdm.write`.

Install with `pip install ".[tqdm]"`.

## Components

| Component | Responsibility |
| --- | --- |
| [renderer.py](renderer.py) | `TqdmRenderer`, driving a `tqdm` instance through the renderer lifecycle. |
| [group_renderer.py](group_renderer.py) | `TqdmGroupRenderer`, placing every bar of a group on a `tqdm` line of its own. |
