"""Live daemon entry point.

Listens on the configured Slack channel in real time, runs Managed Agent
sessions to analyze requirements and plan the backlog, and syncs confirmed
backlogs to Jira.

    python main_live.py
"""
import logging
import sys

from anthropic import Anthropic

from config import ConfigError, load_runtime_config
from integrations.jira_service import JiraService
from integrations.slack_listener import run_forever
from logging_config import configure_logging

logger = logging.getLogger(__name__)


def main() -> int:
    try:
        config = load_runtime_config()
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    configure_logging(config.log_level)

    logger.info("=== GWC Project Management Agent (Claude Managed Agents) — starting ===")
    logger.info("Slack channel: %s", config.slack.channel_id)
    logger.info("Agent: %s | Environment: %s", config.anthropic.agent_id, config.anthropic.environment_id)

    anthropic_client = Anthropic(api_key=config.anthropic.api_key)

    jira = None
    if config.jira:
        try:
            jira = JiraService(config.jira.url, config.jira.email, config.jira.api_token)
            logger.info("Jira integration enabled (%s)", config.jira.url)
        except Exception as exc:  # noqa: BLE001
            logger.error("Jira configured but failed to initialize (%s) — continuing without Jira sync.", exc)
    else:
        logger.info("Jira integration not configured — the agent will analyze and plan, but cannot sync to Jira.")

    try:
        run_forever(config, anthropic_client, jira)
    except Exception:  # noqa: BLE001
        logger.exception("Fatal error in the Slack listener")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
