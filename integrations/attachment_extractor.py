"""Extracts plain text from Slack file attachments (PDF and text-like files)."""
import io
import logging
import urllib.request

from pypdf import PdfReader

logger = logging.getLogger(__name__)

_TEXT_MIME_PREFIXES = ("text/",)
_TEXT_MIME_TYPES = {"application/json", "application/x-javascript", "application/xml"}
_TEXT_EXTENSIONS = (
    ".txt", ".md", ".json", ".xml", ".csv", ".py", ".js", ".ts", ".html", ".css", ".yaml", ".yml",
)


def download_file(url: str, bot_token: str) -> bytes:
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {bot_token}"})
    with urllib.request.urlopen(request) as response:  # noqa: S310 - Slack's own CDN URL
        return response.read()


def extract_text(filename: str, mime_type: str, data: bytes) -> str:
    """Best-effort text extraction. Never raises — returns a descriptive
    placeholder string for unsupported or broken files so the caller can keep
    going without losing the rest of the message content."""
    filename_lower = (filename or "").lower()
    mime_type = mime_type or ""

    if mime_type == "application/pdf" or filename_lower.endswith(".pdf"):
        try:
            reader = PdfReader(io.BytesIO(data))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(p for p in pages if p)
        except Exception as exc:  # noqa: BLE001
            logger.error("Error parsing PDF '%s': %s", filename, exc)
            return f"[Error parsing PDF file {filename}: {exc}]"

    is_text_mime = mime_type.startswith(_TEXT_MIME_PREFIXES) or mime_type in _TEXT_MIME_TYPES
    is_text_ext = filename_lower.endswith(_TEXT_EXTENSIONS)
    if is_text_mime or is_text_ext:
        try:
            return data.decode("utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001
            logger.error("Error decoding text file '%s': %s", filename, exc)
            return f"[Error decoding text file {filename}]"

    return f"[Attached non-text file: {filename} ({mime_type}) — content not extracted]"
