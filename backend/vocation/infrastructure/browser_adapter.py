from __future__ import annotations

import webbrowser
from collections.abc import Callable

from vocation.application.external_navigation import BrowserOpenError


class SystemBrowserAdapter:
    def __init__(self, opener: Callable[[str], bool] | None = None):
        self.opener = opener or webbrowser.open_new_tab

    def open(self, url: str) -> None:
        try:
            opened = self.opener(url)
        except Exception as error:
            raise BrowserOpenError("The system browser failed to open the external link.") from error
        if not opened:
            raise BrowserOpenError("The system browser could not open the external link.")
