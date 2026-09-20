# rich

## Overview

Renders with [rich](https://pypi.org/project/rich/), which produces the most
elaborate output of the supported libraries. A `Progress` instance holds a
single task, and the displayed columns depend on the task: a bar with
percentage, counter and remaining time when the total is known, a spinner with a
counter when it is not.

Install with `pip install ".[rich]"`.

## Components

| Component | Responsibility |
| --- | --- |
| [adapter.py](adapter.py) | `RichAdapter`, driving one task of `rich.progress.Progress`. |
