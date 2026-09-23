"""Tests for the backend resolution rules."""

from __future__ import annotations

import pytest

from progress_bar import (
    BackendResolver,
    ProgressBarBackend,
    RenderEnvironment,
    resolver,
)
from tests.missing_package_stub import MissingPackageStub
from tests.terminal_stream_stub import TerminalStreamStub


class TestBackendResolver:
    """Behaviour of :class:`BackendResolver`."""

    def test_redirected_stream_falls_back_to_plain(self) -> None:
        environment = RenderEnvironment(TerminalStreamStub(is_terminal=False))
        backend_resolver = BackendResolver(environment)
        assert backend_resolver.resolve() is ProgressBarBackend.PLAIN

    def test_built_in_backends_are_always_installed(self) -> None:
        backend_resolver = BackendResolver(RenderEnvironment(TerminalStreamStub()))
        assert backend_resolver.is_installed(ProgressBarBackend.PLAIN)
        assert backend_resolver.is_installed(ProgressBarBackend.SILENT)

    def test_explicit_backend_wins_over_priority(self) -> None:
        environment = RenderEnvironment(TerminalStreamStub())
        backend_resolver = BackendResolver(environment)
        assert backend_resolver.resolve(ProgressBarBackend.PLAIN) is (
            ProgressBarBackend.PLAIN
        )

    def test_automatic_resolution_follows_priority(self) -> None:
        environment = RenderEnvironment(TerminalStreamStub())
        backend_resolver = BackendResolver(
            environment, priority=[ProgressBarBackend.PLAIN]
        )
        assert backend_resolver.resolve() is ProgressBarBackend.PLAIN

    def test_empty_priority_is_rejected(self) -> None:
        with pytest.raises(ValueError):
            BackendResolver(priority=[])

    def test_uninstalled_preference_falls_back_to_plain(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(resolver, "find_spec", MissingPackageStub())
        backend_resolver = BackendResolver(RenderEnvironment(TerminalStreamStub()))
        assert backend_resolver.resolve(ProgressBarBackend.RICH) is (
            ProgressBarBackend.PLAIN
        )

    def test_uninstalled_backends_are_left_out_of_the_listing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(resolver, "find_spec", MissingPackageStub())
        backend_resolver = BackendResolver(RenderEnvironment(TerminalStreamStub()))
        assert backend_resolver.installed_backends() == (
            ProgressBarBackend.PLAIN,
            ProgressBarBackend.SILENT,
        )

    def test_require_reports_the_missing_distribution(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(resolver, "find_spec", MissingPackageStub())
        backend_resolver = BackendResolver(RenderEnvironment(TerminalStreamStub()))
        with pytest.raises(ModuleNotFoundError, match="alive-progress"):
            backend_resolver.require(ProgressBarBackend.ALIVE_PROGRESS)

    def test_require_returns_an_installed_backend(self) -> None:
        backend_resolver = BackendResolver(RenderEnvironment(TerminalStreamStub()))
        assert backend_resolver.require(ProgressBarBackend.PLAIN) is (
            ProgressBarBackend.PLAIN
        )

    def test_group_resolution_keeps_a_supported_preference(self) -> None:
        backend_resolver = BackendResolver(RenderEnvironment(TerminalStreamStub()))
        assert backend_resolver.resolve_group(ProgressBarBackend.PLAIN) is (
            ProgressBarBackend.PLAIN
        )

    def test_group_resolution_replaces_an_unsupported_preference(self) -> None:
        backend_resolver = BackendResolver(RenderEnvironment(TerminalStreamStub()))
        with pytest.warns(UserWarning, match="alive_progress"):
            backend = backend_resolver.resolve_group(ProgressBarBackend.ALIVE_PROGRESS)
        assert backend.is_group_supported

    def test_group_resolution_skips_unsupported_backends_of_the_priority(
        self,
    ) -> None:
        backend_resolver = BackendResolver(
            RenderEnvironment(TerminalStreamStub()),
            priority=[ProgressBarBackend.ALIVE_PROGRESS],
        )
        assert backend_resolver.resolve_group() is ProgressBarBackend.PLAIN

    def test_group_resolution_falls_back_to_plain_on_a_redirected_stream(
        self,
    ) -> None:
        environment = RenderEnvironment(TerminalStreamStub(is_terminal=False))
        assert BackendResolver(environment).resolve_group() is (
            ProgressBarBackend.PLAIN
        )
