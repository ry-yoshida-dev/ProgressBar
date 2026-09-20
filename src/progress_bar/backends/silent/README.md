# silent

## Overview

Counts the reported steps without producing any output. It is selected when the
display is disabled, which keeps calling code free of conditional branches, and
it is the backend used by the tests.

## Components

| Component | Responsibility |
| --- | --- |
| [renderer.py](renderer.py) | `SilentRenderer`, a no-op implementation of the renderer lifecycle. |
