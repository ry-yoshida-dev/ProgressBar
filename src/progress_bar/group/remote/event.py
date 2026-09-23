"""Union of the events a worker process sends to its progress bar group."""

from __future__ import annotations

from progress_bar.group.remote.bar_advanced import RemoteBarAdvanced
from progress_bar.group.remote.bar_finished import RemoteBarFinished
from progress_bar.group.remote.bar_opened import RemoteBarOpened

type RemoteBarEvent = RemoteBarOpened | RemoteBarAdvanced | RemoteBarFinished
