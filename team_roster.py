"""Loads the virtual team roster and formats it for inclusion in a session
kickoff message. Kept out of the agent's static system prompt so the roster
can change without needing to publish a new agent version."""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

_ROSTER_PATH = Path(__file__).resolve().parent / "team_members.json"


def load_roster() -> List[Dict[str, Any]]:
    try:
        with _ROSTER_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not load team_members.json (%s); proceeding with an empty roster.", exc)
        return []


def format_roster_for_prompt() -> str:
    roster = load_roster()
    if not roster:
        return "(no team roster configured — assign stories generically by role only)"
    lines = [
        f"- {m['name']} — {m['role']} (max {m.get('max_story_points', 10)} story points per sprint)"
        for m in roster
    ]
    return "\n".join(lines)
