"""One-time (idempotent) provisioning of the Managed Agent + Environment.

Run via main_setup.py. Safe to re-run: if CMA_AGENT_ID / CMA_ENVIRONMENT_ID
are already set, the existing agent is updated in place (a new version is
published) instead of creating a duplicate agent.

Jira tool *schemas* are part of the agent's base tool set from the moment
it's created — the agent has always been able to see them and their
descriptions, in every turn, from Turn 1 onward. Actually calling them before
manager approval is blocked deterministically in session_manager.py's tool
dispatcher (not by the model's own judgment, and not by a mid-session tool
grant, which testing showed the model does not reliably act on). This split
— tools visible early, execution gated in our own code — is what makes the
"agent knows how to use the tool once told to" behavior reliable while still
keeping a real human-approval gate before anything is written to Jira.
"""
import logging
from pathlib import Path
from typing import Optional, Tuple

from anthropic import Anthropic

from cma.tools import JIRA_TOOL_DEFINITIONS

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

AGENT_NAME = "GWC Project Management Agent"
ENVIRONMENT_NAME = "gwc-pm-agent-environment"

# All tools, including Jira, are present from session creation onward so the
# model has them in context the whole conversation. Whether a Jira tool call
# is actually *allowed to execute* is enforced in session_manager.py's tool
# dispatcher based on the current turn's approval state — not by whether the
# tool is merely present in this list.
BASE_TOOLS = [{"type": "agent_toolset_20260401"}] + JIRA_TOOL_DEFINITIONS


def build_system_prompt() -> str:
    parts = [
        (PROMPTS_DIR / "system_prompt.md").read_text(encoding="utf-8"),
        "\n\n---\n\n# Requirements Analysis Methodology (reference)\n\n",
        (PROMPTS_DIR / "requirements_analysis.md").read_text(encoding="utf-8"),
        "\n\n---\n\n# Backlog Planning Methodology (reference)\n\n",
        (PROMPTS_DIR / "backlog_planning.md").read_text(encoding="utf-8"),
    ]
    return "".join(parts)


def ensure_environment(client: Anthropic, environment_id: Optional[str]) -> str:
    if environment_id:
        try:
            env = client.beta.environments.retrieve(environment_id)
            logger.info("Reusing existing environment %s", env.id)
            return env.id
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "CMA_ENVIRONMENT_ID=%s could not be retrieved (%s); creating a new environment.",
                environment_id, exc,
            )

    env = client.beta.environments.create(
        name=ENVIRONMENT_NAME,
        config={"type": "cloud", "networking": {"type": "unrestricted"}},
    )
    logger.info("Created new environment %s", env.id)
    return env.id


def ensure_agent(
    client: Anthropic,
    agent_id: Optional[str],
    model: str,
    effort: str,
) -> Tuple[str, int]:
    system_prompt = build_system_prompt()
    model_config = {"id": model, "effort": effort}

    if agent_id:
        try:
            current = client.beta.agents.retrieve(agent_id)
            updated = client.beta.agents.update(
                agent_id,
                version=current.version,
                model=model_config,
                system=system_prompt,
                tools=BASE_TOOLS,
            )
            logger.info("Updated existing agent %s to version %s", updated.id, updated.version)
            return updated.id, updated.version
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "CMA_AGENT_ID=%s could not be updated (%s); creating a new agent.",
                agent_id, exc,
            )

    created = client.beta.agents.create(
        name=AGENT_NAME,
        model=model_config,
        system=system_prompt,
        tools=BASE_TOOLS,
        description=(
            "Analyzes Slack project requirements into a spec + Agile backlog, "
            "then syncs the confirmed backlog to Jira as Epics/Stories/Sub-tasks."
        ),
    )
    logger.info("Created new agent %s (version %s)", created.id, created.version)
    return created.id, created.version


def provision(client: Anthropic, model: str, effort: str, agent_id: Optional[str], environment_id: Optional[str]):
    """Returns (agent_id, agent_version, environment_id)."""
    env_id = ensure_environment(client, environment_id)
    resolved_agent_id, agent_version = ensure_agent(client, agent_id, model, effort)
    return resolved_agent_id, agent_version, env_id
