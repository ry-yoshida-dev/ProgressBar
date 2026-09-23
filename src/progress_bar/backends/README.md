# backends

## Overview

One sub-package per rendering technique, each translating the
`ProgressRenderer` lifecycle (`_open`, `_render`, `_close`) into the API of its
library, and, except for `alive_progress`, the `ProgressGroupRenderer` lifecycle
of a group of concurrent bars. A sub-package imports its third-party library at
module level and is itself imported on demand by `RendererFactory` and
`GroupRendererFactory`, so an uninstalled optional
package never breaks an unrelated backend. The renderer classes are also exposed
lazily from this package, which keeps `import progress_bar.backends` free of
optional dependencies.

## Components

| Component | Responsibility |
| --- | --- |
| [tqdm/](tqdm/) | Backend rendering with `tqdm.auto.tqdm`. |
| [progressbar2/](progressbar2/) | Backend rendering with `progressbar.ProgressBar` and `progressbar.MultiBar`. |
| [alive_progress/](alive_progress/) | Backend rendering with the `alive_bar` context manager. |
| [rich/](rich/) | Backend rendering the tasks of a `rich.progress.Progress`. |
| [plain/](plain/) | Dependency-free backend for terminals and log files. |
| [silent/](silent/) | Backend counting steps without producing output. |
