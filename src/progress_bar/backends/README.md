# backends

## Overview

One sub-package per rendering technique, each adapting a library to `ProgressRenderer` and, except for
`alive_progress`, to `ProgressGroupRenderer` for groups of bars. Sub-packages are imported on demand, so an uninstalled
optional library never breaks another backend.

## Components

| Component | Responsibility |
| --- | --- |
| [tqdm/](tqdm/README.md) | Backend rendering with `tqdm.auto.tqdm`. |
| [progressbar2/](progressbar2/README.md) | Backend rendering with `progressbar.ProgressBar` and `progressbar.MultiBar`. |
| [alive_progress/](alive_progress/README.md) | Backend rendering with the `alive_bar` context manager. |
| [rich/](rich/README.md) | Backend rendering the tasks of a `rich.progress.Progress`. |
| [plain/](plain/README.md) | Dependency-free backend for terminals and log files. |
| [silent/](silent/README.md) | Backend counting steps without producing output. |
