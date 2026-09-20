# tests

## Overview

Pytest suite covering backend metadata, resolution rules, the tracker lifecycle
and the rendering of every backend. The core tests never rely on an optional
library being installed: they use the silent and plain backends with a stubbed
output stream, and a stubbed module lookup when an uninstalled package has to
be simulated. The adapters of the optional libraries are exercised when their
package is present and skipped otherwise.

Run them with `pytest` from the repository root.

## Components

| Component | Responsibility |
| --- | --- |
| [terminal_stream_stub.py](terminal_stream_stub.py) | `TerminalStreamStub`, an in-memory stream with a configurable `isatty()`. |
| [missing_package_stub.py](missing_package_stub.py) | `MissingPackageStub`, a `find_spec` replacement reporting every package as missing. |
| [test_backend.py](test_backend.py) | Module and distribution names exposed by `ProgressBarBackend`. |
| [test_resolver.py](test_resolver.py) | Priority, environment fallback and `require()` behaviour of `BackendResolver`. |
| [test_tracker.py](test_tracker.py) | Lifecycle, total inference and error handling of `ProgressTracker`. |
| [test_plain_adapter.py](test_plain_adapter.py) | Terminal, log file and transient rendering of `PlainAdapter`. |
| [test_third_party_adapters.py](test_third_party_adapters.py) | Lifecycle of the adapters wrapping an optional library, skipped when it is missing. |
