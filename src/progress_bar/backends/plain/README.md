# plain

## Overview

Renders a textual bar without any third-party package, which makes it the
fallback that can never fail. On an interactive terminal the line is redrawn in
place; on a redirected stream a line is emitted only when a milestone is
reached, so log files stay readable, and the final state is written once
instead of repeating the last milestone.

The group renderer keeps the running bars of a group in a block of lines that is
redrawn in place with ANSI cursor movement, throttled while steps arrive, and
writes a finished bar that stays visible once above the block. On a redirected
stream every bar logs its own milestones, labelled with its description.

## Components

| Component | Responsibility |
| --- | --- |
| [renderer.py](renderer.py) | `PlainRenderer`, formatting and writing the bar to the output stream. |
| [group_renderer.py](group_renderer.py) | `PlainGroupRenderer`, redrawing the bars of a group as one block of lines. |
| [formatter.py](formatter.py) | `PlainBarFormatter`, the line format and logging milestones shared by both renderers. |
