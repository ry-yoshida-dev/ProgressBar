"""Tests for the backend enum."""

from __future__ import annotations

from progress_bar import ProgressBarBackend


class TestProgressBarBackend:
    """Behaviour of :class:`ProgressBarBackend`."""

    def test_third_party_backends_expose_import_and_install_names(self) -> None:
        assert ProgressBarBackend.PROGRESSBAR2.module_name == "progressbar"
        assert ProgressBarBackend.PROGRESSBAR2.distribution_name == "progressbar2"
        assert ProgressBarBackend.ALIVE_PROGRESS.distribution_name == "alive-progress"

    def test_built_in_backends_need_no_package(self) -> None:
        assert not ProgressBarBackend.PLAIN.is_third_party
        assert not ProgressBarBackend.SILENT.is_third_party
        assert ProgressBarBackend.RICH.is_third_party

    def test_only_alive_progress_cannot_display_a_group(self) -> None:
        unsupported = [
            backend for backend in ProgressBarBackend if not backend.is_group_supported
        ]
        assert unsupported == [ProgressBarBackend.ALIVE_PROGRESS]
