import os
import uuid
from pathlib import Path

from app.contracts.object_storage import ObjectStorage


class LocalStorage(ObjectStorage):
    def __init__(self, base_path: str = "storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def upload(
        self,
        bucket: str,
        key: str,
        data: bytes,
        content_type: str | None = None,
        **kwargs,
    ) -> str:
        bucket_path = self.base_path / bucket
        bucket_path.mkdir(parents=True, exist_ok=True)

        file_path = bucket_path / key
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(data)

        return str(file_path)

    async def download(
        self,
        bucket: str,
        key: str,
        **kwargs,
    ) -> bytes:
        file_path = self.base_path / bucket / key

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as f:
            return f.read()

    async def delete(
        self,
        bucket: str,
        key: str,
        **kwargs,
    ) -> bool:
        file_path = self.base_path / bucket / key

        if file_path.exists():
            file_path.unlink()
            return True
        return False

    async def get_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600,
        **kwargs,
    ) -> str:
        file_path = self.base_path / bucket / key
        return str(file_path.absolute())

    def health_check(self) -> bool:
        return self.base_path.exists()
