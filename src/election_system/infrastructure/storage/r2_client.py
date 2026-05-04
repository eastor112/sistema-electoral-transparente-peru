"""Cloudflare R2 storage adapter (S3-compatible via boto3)."""

import asyncio
import mimetypes
import uuid
from functools import partial
from typing import TYPE_CHECKING

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from election_system.core.config import settings
from election_system.core.exceptions import InvalidAssetError, StorageError

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client

MAX_UPLOAD_BYTES: int = 5 * 1024 * 1024  # 5 MB

_ALLOWED_CONTENT_TYPES: frozenset[str] = frozenset(
    {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/svg+xml",
    }
)


def _check_magic_bytes(data: bytes, content_type: str) -> bool:
    """Verify file content matches the declared content type via magic bytes.

    Prevents content-type spoofing attacks (e.g. disguising HTML/JS as JPEG).
    """
    if content_type == "image/jpeg":
        return data[:3] == b"\xff\xd8\xff"
    if content_type == "image/png":
        return data[:8] == b"\x89PNG\r\n\x1a\n"
    if content_type == "image/webp":
        return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    if content_type == "image/svg+xml":
        snippet = data[:256].lstrip()
        return snippet.startswith((b"<svg", b"<?xml", b"<SVG"))
    return False


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

        Validates content type, size, and magic bytes before uploading.
        """
        if content_type not in _ALLOWED_CONTENT_TYPES:
            raise InvalidAssetError(
                f"Content type {content_type!r} is not allowed. "
                f"Accepted: {sorted(_ALLOWED_CONTENT_TYPES)}"
            )
        if len(data) > MAX_UPLOAD_BYTES:
            raise InvalidAssetError(
                f"File exceeds maximum allowed size of {MAX_UPLOAD_BYTES // 1024 // 1024} MB."
            )
        if not _check_magic_bytes(data, content_type):
            raise InvalidAssetError(
                "File content does not match the declared content type. "
                "Ensure the file is a valid image."
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
