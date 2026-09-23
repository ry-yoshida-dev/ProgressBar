# tests

## Overview

Pytest suite covering backend metadata, resolution rules, the reporter and group
lifecycles, bars of worker processes and the rendering of every backend. The core tests never rely on an optional
library being installed: they use the silent and plain backends with a stubbed
output stream, and a stubbed module lookup when an uninstalled package has to
be simulated. The renderers of the optional libraries are exercised when their
package is present and skipped otherwise.

Run them with `pytest` from the repository root.

## Components

| Component | Responsibility |
| --- | --- |
| [terminal_stream_stub.py](terminal_stream_stub.py) | `TerminalStreamStub`, an in-memory stream with a configurable `isatty()`. |
| [missing_package_stub.py](missing_package_stub.py) | `MissingPackageStub`, a `find_spec` replacement reporting every package as missing. |
| [remote_worker_stub.py](remote_worker_stub.py) | `RemoteWorkerStub`, a process pool initializer and task reporting to a remote group. |
| [test_backend.py](test_backend.py) | Module and distribution names exposed by `ProgressBarBackend`. |
| [test_resolver.py](test_resolver.py) | Priority, environment fallback and `require()` behaviour of `BackendResolver`. |
| [test_reporter.py](test_reporter.py) | Lifecycle, total inference and error handling of `ProgressBarReporter`. |
| [test_plain_renderer.py](test_plain_renderer.py) | Terminal, log file and transient rendering of `PlainRenderer`. |
| [test_third_party_renderers.py](test_third_party_renderers.py) | Lifecycle of the single and group renderers wrapping an optional library, skipped when it is missing. |
| [test_group.py](test_group.py) | Lifecycle, thread safety and backend replacement of `ProgressBarGroup` and its bars. |
| [test_plain_group_renderer.py](test_plain_group_renderer.py) | Terminal block redraws and per-bar log lines of `PlainGroupRenderer`. |
| [test_remote.py](test_remote.py) | Step coalescing of `RemoteProgressBar` and rendering of worker-process bars by the parent group. |
