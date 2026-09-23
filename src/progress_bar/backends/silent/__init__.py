"""Backend that counts steps without producing output."""

from progress_bar.backends.silent.group_renderer import SilentGroupRenderer
from progress_bar.backends.silent.renderer import SilentRenderer

__all__ = ["SilentGroupRenderer", "SilentRenderer"]
