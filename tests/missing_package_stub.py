"""Test double for module lookup in an interpreter without optional packages."""

from __future__ import annotations

from importlib.machinery import ModuleSpec


class MissingPackageStub:
    """Replacement for :func:`importlib.util.find_spec` that finds nothing.

    Patching it into :mod:`progress_bar.resolver` makes every optional
    backend look uninstalled, whichever packages the test run has.
    """

    def __call__(self, name: str, package: str | None = None) -> ModuleSpec | None:
        """Report ``name`` as not importable.

        Parameters
        ----------
        name
            Module the resolver looks for.
        package
            Anchor of a relative import, accepted for signature
            compatibility and never used.
        """
        return None
