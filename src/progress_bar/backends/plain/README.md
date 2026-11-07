# plain

## Overview

Renders a textual bar without any third-party package; the fallback that never fails.

## Components

| Component | Responsibility |
| --- | --- |
| [renderer.py](renderer.py) | `PlainRenderer`, formatting and writing the bar to the output stream. |
| [group_renderer.py](group_renderer.py) | `PlainGroupRenderer`, redrawing the bars of a group as one block of lines. |
| [formatter.py](formatter.py) | `PlainBarFormatter`, the line format and logging milestones shared by both renderers. |
