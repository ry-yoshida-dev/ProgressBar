# silent

## Overview

Counts the reported steps without producing any output; used when the display is disabled.

## Components

| Component | Responsibility |
| --- | --- |
| [renderer.py](renderer.py) | `SilentRenderer`, a no-op implementation of the renderer lifecycle. |
| [group_renderer.py](group_renderer.py) | `SilentGroupRenderer`, a no-op implementation of the group renderer lifecycle. |
