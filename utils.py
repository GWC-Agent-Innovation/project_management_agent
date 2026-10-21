"""Small shared helpers: JSON state persistence and safe filename derivation."""
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def load_json_state(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:  # noqa: BLE001
        logger.error("Could not read state file %s (%s) — starting with empty state.", path, exc)
        return {}


def save_json_state(path: Path, data: Dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        tmp_path.replace(path)
    except Exception as exc:  # noqa: BLE001
        logger.error("Could not write state file %s: %s", path, exc)


def clean_project_filename(markdown_text: str, default_filename: str = "project_details.md") -> str:
    """Derives a safe filename from the first H1 title in generated markdown."""
    lines = [line.strip() for line in markdown_text.split("\n") if line.strip()]
    title = None
    for i, line in enumerate(lines):
        if re.match(r"^#+\s*\*?Project Title\*?$", line, re.IGNORECASE):
            if i + 1 < len(lines):
                candidate = lines[i + 1].strip()
                if not re.match(r"^[=\-]+$", candidate):
                    title = candidate
                    break
                if i + 2 < len(lines):
                    title = lines[i + 2].strip()
                    break
        elif line.startswith("#"):
            candidate = re.sub(r"[#*_]", "", line).strip()
            if candidate.lower() not in ("project title", "project overview"):
                title = candidate
                break

    if not title:
        return default_filename

    clean = re.sub(r"[^\w\s-]", "", title).strip()
    clean = re.sub(r"[-\s]+", "_", clean)
    if len(clean) > 60:
        clean = clean[:60].rstrip("_")
    return f"{clean}.md" if clean else default_filename


_ISSUE_KEY_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,9})-\d+\b")


def extract_first_project_key(text: str) -> Optional[str]:
    """Finds the first Jira-style issue key (e.g. KAN-123) in text and returns
    its project-key prefix (e.g. KAN)."""
    match = _ISSUE_KEY_RE.search(text or "")
    return match.group(1) if match else None
