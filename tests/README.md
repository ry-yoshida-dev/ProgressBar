# tests

## Overview

Pytest suite covering backend metadata, resolution rules, the reporter lifecycle
and the rendering of every backend. The core tests never rely on an optional
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
| [test_backend.py](test_backend.py) | Module and distribution names exposed by `ProgressBarBackend`. |
| [test_resolver.py](test_resolver.py) | Priority, environment fallback and `require()` behaviour of `BackendResolver`. |
| [test_reporter.py](test_reporter.py) | Lifecycle, total inference and error handling of `ProgressBarReporter`. |
| [test_plain_renderer.py](test_plain_renderer.py) | Terminal, log file and transient rendering of `PlainRenderer`. |
| [test_third_party_renderers.py](test_third_party_renderers.py) | Lifecycle of the renderers wrapping an optional library, skipped when it is missing. |
