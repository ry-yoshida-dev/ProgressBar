# backends

## Overview

One sub-package per rendering technique, each translating the
`ProgressReporter` lifecycle (`_open`, `_render`, `_close`) into the API of its
library. A sub-package imports its third-party library at module level and is
itself imported on demand by `ReporterFactory`, so an uninstalled optional
package never breaks an unrelated backend. The adapter classes are also exposed
lazily from this package, which keeps `import progress_bar.backends` free of
optional dependencies.

## Components

| Component | Responsibility |
| --- | --- |
| [tqdm/](tqdm/) | Backend rendering with `tqdm.auto.tqdm`. |
| [progressbar2/](progressbar2/) | Backend rendering with `progressbar.ProgressBar`. |
| [alive_progress/](alive_progress/) | Backend rendering with the `alive_bar` context manager. |
| [rich/](rich/) | Backend rendering a single task of `rich.progress.Progress`. |
| [plain/](plain/) | Dependency-free backend for terminals and log files. |
| [silent/](silent/) | Backend counting steps without producing output. |
