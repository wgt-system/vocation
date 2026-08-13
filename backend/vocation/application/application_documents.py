from __future__ import annotations

from typing import Protocol


class ApplicationDocumentStore(Protocol):
    def write(self, storage_ref: str, payload: bytes) -> None: ...

    def read(self, storage_ref: str) -> bytes: ...
