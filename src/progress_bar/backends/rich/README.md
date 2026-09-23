# rich

## Overview

Renders with [rich](https://pypi.org/project/rich/), which produces the most
elaborate output of the supported libraries. A `Progress` instance holds a
single task, and the displayed columns depend on the task: a bar with
percentage, counter and remaining time when the total is known, a spinner with a
counter when it is not.

`rich` allows one live display per console, so a group shares a single
`Progress` and each of its bars is a task. Descriptions are escaped, so text in
square brackets is shown as written instead of being read as markup.

Install with `pip install ".[rich]"`.

## Components

| Component | Responsibility |
| --- | --- |
| [renderer.py](renderer.py) | `RichRenderer`, driving one task of `rich.progress.Progress`. |
| [group_renderer.py](group_renderer.py) | `RichGroupRenderer`, drawing every bar of a group as a task of one `Progress`. |
