"""Cloudflare R2 storage adapter (S3-compatible via boto3)."""

import asyncio
import mimetypes
import uuid
from functools import partial
from typing import TYPE_CHECKING

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from election_system.core.config import settings
from election_system.core.exceptions import StorageError

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client

_ALLOWED_CONTENT_TYPES: frozenset[str] = frozenset(
    {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/svg+xml",
    }
)
_MAX_BYTES: int = 5 * 1024 * 1024  # 5 MB


def _build_s3_client() -> "S3Client":
    return boto3.client(
        "s3",
        endpoint_url=settings.r2_endpoint_url or None,
        aws_access_key_id=settings.r2_access_key_id or None,
        aws_secret_access_key=settings.r2_secret_access_key or None,
        region_name="auto",
    )


class R2StorageAdapter:
    """Async wrapper around boto3 S3 client targeting Cloudflare R2."""

    def __init__(self) -> None:
        self._client: S3Client = _build_s3_client()
        self._bucket: str = settings.r2_bucket_name

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def _public_url(self, key: str) -> str:
        base = settings.r2_public_url.rstrip("/")
        if base:
            return f"{base}/{key}"
        # Fallback to path-style URL when no public URL is configured (dev)
        endpoint = (settings.r2_endpoint_url or "https://r2.example.com").rstrip("/")
        return f"{endpoint}/{self._bucket}/{key}"

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------

    async def upload_image(
        self,
        *,
        folder: str,
        data: bytes,
        content_type: str,
        original_filename: str = "",
    ) -> str:
        """Upload image bytes to R2 and return the public URL.

        Validates content type and size before uploading.
        """
        if content_type not in _ALLOWED_CONTENT_TYPES:
            from election_system.core.exceptions import InvalidAssetError

            raise InvalidAssetError(
                f"Content type {content_type!r} is not allowed. "
                f"Accepted: {sorted(_ALLOWED_CONTENT_TYPES)}"
            )
        if len(data) > _MAX_BYTES:
            from election_system.core.exceptions import InvalidAssetError

            raise InvalidAssetError(
                f"File exceeds maximum allowed size of {_MAX_BYTES // 1024 // 1024} MB."
            )

        ext = _ext_from_content_type(content_type, original_filename)
        key = f"{folder.strip('/')}/{uuid.uuid4().hex}{ext}"

        fn = partial(
            self._client.put_object,
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        try:
            await asyncio.to_thread(fn)
        except (BotoCoreError, ClientError) as exc:
            raise StorageError(f"Failed to upload object to R2: {exc}") from exc

        return self._public_url(key)

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    async def delete_object(self, *, key: str) -> None:
        fn = partial(self._client.delete_object, Bucket=self._bucket, Key=key)
        try:
            await asyncio.to_thread(fn)
        except (BotoCoreError, ClientError) as exc:
            raise StorageError(f"Failed to delete object from R2: {exc}") from exc


def _ext_from_content_type(content_type: str, original_filename: str) -> str:
    if original_filename:
        dot = original_filename.rfind(".")
        if dot != -1:
            return original_filename[dot:].lower()
    ext = mimetypes.guess_extension(content_type)
    # mimetypes may return .jpe instead of .jpg
    _overrides = {".jpe": ".jpg", ".jpeg": ".jpg"}
    return _overrides.get(ext or "", ext or "")


# Singleton — instantiated lazily per process
_adapter: R2StorageAdapter | None = None


def get_r2_adapter() -> R2StorageAdapter:
    global _adapter
    if _adapter is None:
        _adapter = R2StorageAdapter()
    return _adapter
