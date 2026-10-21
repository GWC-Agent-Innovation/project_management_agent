"""Centralized configuration loading and validation.

Two validation levels are exposed because the project has two entry points
with different requirements:
  - main_setup.py only needs an Anthropic API key (it provisions the agent
    and environment once, before Slack/Jira are necessarily configured).
  - main_live.py needs Slack + Anthropic + the agent/environment IDs that
    main_setup.py produces. Jira is optional: if it isn't configured the
    agent still analyzes requirements and drafts a backlog, it just can't
    sync to Jira.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


def _load_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class AnthropicConfig:
    api_key: str
    model: str
    effort: str
    agent_id: Optional[str]
    environment_id: Optional[str]


@dataclass(frozen=True)
class SlackConfig:
    bot_token: str
    app_token: str
    channel_id: str


@dataclass(frozen=True)
class JiraConfig:
    url: str
    email: str
    api_token: str
    default_project_key: str


@dataclass(frozen=True)
class RuntimeConfig:
    anthropic: AnthropicConfig
    slack: SlackConfig
    jira: Optional[JiraConfig]
    output_file_path: str
    state_dir: Path
    log_level: str


_PLACEHOLDER_MARKERS = (
    "replace-with-your",
    "your-domain",
    "your-email",
    "C0000000000",
)


def _is_placeholder(value: Optional[str]) -> bool:
    if not value:
        return True
    return any(marker in value for marker in _PLACEHOLDER_MARKERS)


def load_setup_config() -> AnthropicConfig:
    """Minimal config needed to run main_setup.py (provision the agent/environment)."""
    _load_env()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if _is_placeholder(api_key):
        raise ConfigError(
            "ANTHROPIC_API_KEY is missing or still a placeholder. "
            "Copy .env.example to .env and fill in your real Anthropic API key."
        )
    return AnthropicConfig(
        api_key=api_key,
        model=os.getenv("CMA_MODEL", "claude-sonnet-5"),
        effort=os.getenv("CMA_EFFORT", "high"),
        agent_id=(os.getenv("CMA_AGENT_ID") or "").strip("'\" \t\r\n") or None,
        environment_id=(os.getenv("CMA_ENVIRONMENT_ID") or "").strip("'\" \t\r\n") or None,
    )


def load_runtime_config() -> RuntimeConfig:
    """Full config needed to run main_live.py (the Slack daemon)."""
    _load_env()

    missing = []

    bot_token = os.getenv("SLACK_BOT_TOKEN")
    if _is_placeholder(bot_token):
        missing.append("SLACK_BOT_TOKEN")

    app_token = os.getenv("SLACK_APP_TOKEN")
    if _is_placeholder(app_token):
        missing.append("SLACK_APP_TOKEN")

    channel_id = os.getenv("SLACK_CHANNEL_ID")
    if _is_placeholder(channel_id):
        missing.append("SLACK_CHANNEL_ID")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if _is_placeholder(api_key):
        missing.append("ANTHROPIC_API_KEY")

    agent_id = (os.getenv("CMA_AGENT_ID") or "").strip("'\" \t\r\n")
    environment_id = (os.getenv("CMA_ENVIRONMENT_ID") or "").strip("'\" \t\r\n")
    if not agent_id or not environment_id:
        missing.append("CMA_AGENT_ID / CMA_ENVIRONMENT_ID (run `python main_setup.py` first)")

    if missing:
        raise ConfigError(
            "Missing required configuration: " + ", ".join(missing) +
            ". Fill these in your .env file."
        )

    anthropic_cfg = AnthropicConfig(
        api_key=api_key,
        model=os.getenv("CMA_MODEL", "claude-sonnet-5"),
        effort=os.getenv("CMA_EFFORT", "high"),
        agent_id=agent_id,
        environment_id=environment_id,
    )
    slack_cfg = SlackConfig(bot_token=bot_token, app_token=app_token, channel_id=channel_id)

    jira_url = os.getenv("JIRA_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_token = os.getenv("JIRA_API_TOKEN")
    jira_cfg: Optional[JiraConfig] = None
    if not any(_is_placeholder(v) for v in (jira_url, jira_email, jira_token)):
        jira_cfg = JiraConfig(
            url=jira_url,
            email=jira_email,
            api_token=jira_token,
            default_project_key=os.getenv("JIRA_PROJECT_KEY", "").strip() or "PROJ",
        )

    state_dir = PROJECT_ROOT / os.getenv("STATE_DIR", "state")
    state_dir.mkdir(parents=True, exist_ok=True)

    return RuntimeConfig(
        anthropic=anthropic_cfg,
        slack=slack_cfg,
        jira=jira_cfg,
        output_file_path=os.getenv("OUTPUT_FILE_PATH", "project_details.md"),
        state_dir=state_dir,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
