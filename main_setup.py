"""One-time provisioning script.

Run this once (and again any time you edit the prompt files under
cma/prompts/) to create — or update in place — the Managed Agent and its
Environment, then persist the resulting IDs into .env.

    python main_setup.py
"""
import logging
import sys
from pathlib import Path

from anthropic import Anthropic
from dotenv import set_key

from cma.agent_setup import provision
from config import ConfigError, load_setup_config
from logging_config import configure_logging

logger = logging.getLogger(__name__)

ENV_PATH = Path(__file__).resolve().parent / ".env"


def main() -> int:
    if not ENV_PATH.exists():
        print(
            "No .env file found. Copy .env.example to .env and fill in at least "
            "ANTHROPIC_API_KEY before running this script.",
            file=sys.stderr,
        )
        return 1

    try:
        anthropic_cfg = load_setup_config()
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    configure_logging("INFO")

    client = Anthropic(api_key=anthropic_cfg.api_key)

    logger.info("Provisioning Managed Agent + Environment (model=%s, effort=%s)...",
                anthropic_cfg.model, anthropic_cfg.effort)
    try:
        agent_id, agent_version, environment_id = provision(
            client,
            model=anthropic_cfg.model,
            effort=anthropic_cfg.effort,
            agent_id=anthropic_cfg.agent_id,
            environment_id=anthropic_cfg.environment_id,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Provisioning failed")
        print(f"Provisioning failed: {exc}", file=sys.stderr)
        return 1

    set_key(str(ENV_PATH), "CMA_AGENT_ID", agent_id.strip(), quote_mode="never")
    set_key(str(ENV_PATH), "CMA_ENVIRONMENT_ID", environment_id.strip(), quote_mode="never")

    print("\nProvisioning complete.")
    print(f"  Agent:       {agent_id} (version {agent_version})")
    print(f"  Environment: {environment_id}")
    print(f"  Saved to:    {ENV_PATH}")
    print("\nFill in SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SLACK_CHANNEL_ID, and (optionally) the")
    print("JIRA_* variables in .env, then run: python main_live.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
