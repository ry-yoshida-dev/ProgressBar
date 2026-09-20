# plain

## Overview

Renders a textual bar without any third-party package, which makes it the
fallback that can never fail. On an interactive terminal the line is redrawn in
place; on a redirected stream a line is emitted only when a milestone is
reached, so log files stay readable, and the final state is written once
instead of repeating the last milestone.

## Components

| Component | Responsibility |
| --- | --- |
| [renderer.py](renderer.py) | `PlainRenderer`, formatting and writing the bar to the output stream. |
