from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

from vocation.application.application_documents import (
    ApplicationDocumentPayloadConflictError,
    ApplicationDocumentPayloadNotFoundError,
)


class FilesystemApplicationDocumentStore:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, storage_ref: str, payload: bytes) -> None:
        storage_ref = self._storage_ref(storage_ref)
        if not isinstance(payload, bytes):
            raise TypeError("Application Document payload must be bytes.")
        target = self._path(storage_ref)
        if target.exists():
            raise ApplicationDocumentPayloadConflictError("Application Document storage reference already exists.")

        temporary_path: Path | None = None
        try:
            descriptor, temporary_name = tempfile.mkstemp(prefix=".application-document-", dir=self.root)
            temporary_path = Path(temporary_name)
            with os.fdopen(descriptor, "wb") as temporary_file:
                temporary_file.write(payload)
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            try:
                os.link(temporary_path, target)
            except FileExistsError as error:
                raise ApplicationDocumentPayloadConflictError("Application Document storage reference already exists.") from error
            temporary_path.unlink()
            temporary_path = None
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def read(self, storage_ref: str) -> bytes:
        path = self._path(self._storage_ref(storage_ref))
        if not path.is_file():
            raise ApplicationDocumentPayloadNotFoundError("Application Document payload was not found.")
        return path.read_bytes()

    @staticmethod
    def _storage_ref(value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("storage_ref must be nonempty.")
        return value

    def _path(self, storage_ref: str) -> Path:
        digest = hashlib.sha256(storage_ref.encode("utf-8")).hexdigest()
        return self.root / digest
