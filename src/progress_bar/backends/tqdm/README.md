# tqdm

## Overview

Renders with [tqdm](https://pypi.org/project/tqdm/), the most widespread
progress bar library. `tqdm.auto` is used, so the notebook widget is picked up
automatically when the code runs inside Jupyter. An unknown total is supported
natively and falls back to a running counter.

Install with `pip install ".[tqdm]"`.

## Components

| Component | Responsibility |
| --- | --- |
| [renderer.py](renderer.py) | `TqdmRenderer`, driving a `tqdm` instance through the renderer lifecycle. |
