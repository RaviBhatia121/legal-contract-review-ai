import hashlib
import os
import re
import tempfile

from fastapi import UploadFile

from app.api.errors import file_too_large, unsupported_file_type
from app.core.config import get_settings

_ALLOWED_EXTENSIONS = {".pdf", ".docx"}
_ALLOWED_MIME_TYPES = {
    ".pdf": {"application/pdf"},
    ".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
}
_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]")


def sanitize_display_name(filename: str) -> str:
    name = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    name = _SAFE_NAME_RE.sub("_", name)
    return name[:255] or "upload"


def _extension_of(filename: str) -> str:
    return "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


async def validate_and_read_upload(file: UploadFile) -> tuple[bytes, str, str]:
    """Validate extension/MIME/size and return (content, sanitized_display_name, extension)."""
    settings = get_settings()
    original_name = file.filename or "upload"
    extension = _extension_of(original_name)

    if extension not in _ALLOWED_EXTENSIONS:
        raise unsupported_file_type()

    if file.content_type not in _ALLOWED_MIME_TYPES[extension]:
        raise unsupported_file_type()

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise file_too_large()

    return content, sanitize_display_name(original_name), extension


def write_temp_upload(content: bytes, extension: str) -> str:
    """Write validated upload bytes to a server-generated temp path for the job runner to parse.

    The filename is never derived from client input; only the validated
    extension is reused. Permissions are restricted to the owner.
    """
    settings = get_settings()
    os.makedirs(settings.upload_temp_dir, exist_ok=True)
    fd, path = tempfile.mkstemp(suffix=extension, dir=settings.upload_temp_dir)
    os.chmod(path, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(content)
    return path


def delete_temp_upload(path: str | None) -> None:
    if not path:
        return
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    except OSError:
        pass


def sha256_hex(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
