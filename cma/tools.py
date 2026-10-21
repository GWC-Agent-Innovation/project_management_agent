"""Custom client-side tool definitions the Managed Agent can call, and the
dispatcher that executes them against our own JiraService.

These are declared as `type: custom` tools on the agent (see agent_setup.py).
When the agent emits an `agent.custom_tool_use` event, session_manager.py
routes it to `execute_tool` below and sends the JSON string result back as a
`user.custom_tool_result` event. The Jira API token never enters the agent's
sandbox — only these structured inputs/outputs cross the boundary.
"""
import json
import logging
from typing import Any, Dict

from integrations.jira_service import JiraService, JiraServiceError

logger = logging.getLogger(__name__)

# Tool schemas registered on the agent alongside the built-in agent_toolset.
JIRA_TOOL_DEFINITIONS = [
    {
        "type": "custom",
        "name": "jira_ensure_project",
        "description": (
            "Verify that a Jira project with the given key exists, creating it as a "
            "Kanban software project if it does not. Call this once per sync, before "
            "creating any Epics. Returns {project_key, existed, created, url} — use the "
            "returned `url` verbatim as the Jira board link; never construct or guess a URL yourself."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "project_key": {"type": "string", "description": "2-5 uppercase alphanumeric characters, e.g. KAN"},
                "project_name": {"type": "string", "description": "Human-readable project name"},
            },
            "required": ["project_key", "project_name"],
        },
    },
    {
        "type": "custom",
        "name": "jira_create_epic",
        "description": "Create an Epic issue in Jira under the given project. Returns the new Epic's issue key.",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_key": {"type": "string"},
                "name": {"type": "string", "description": "Short epic name, e.g. 'User Authentication'"},
                "summary": {"type": "string", "description": "One or two sentence description of the epic"},
            },
            "required": ["project_key", "name", "summary"],
        },
    },
    {
        "type": "custom",
        "name": "jira_create_story",
        "description": (
            "Create a Story issue in Jira under a given Epic. Include acceptance criteria in the "
            "description. Returns the new Story's issue key."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "project_key": {"type": "string"},
                "summary": {"type": "string", "description": "The user story statement"},
                "description": {"type": "string", "description": "Full description including acceptance criteria"},
                "epic_key": {"type": "string", "description": "Issue key of the parent Epic"},
                "story_points": {"type": "integer", "description": "Fibonacci story points: 1, 2, 3, 5, 8, or 13"},
                "assignee_name": {"type": "string", "description": "Name of the team member assigned"},
                "assignee_role": {"type": "string", "description": "Role of the assigned team member"},
            },
            "required": ["project_key", "summary", "description", "epic_key", "story_points"],
        },
    },
    {
        "type": "custom",
        "name": "jira_create_subtask",
        "description": "Create a technical Sub-task under a Story. Returns the new Sub-task's issue key.",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_key": {"type": "string"},
                "summary": {"type": "string", "description": "The technical task description"},
                "parent_key": {"type": "string", "description": "Issue key of the parent Story"},
                "assignee_name": {"type": "string"},
            },
            "required": ["project_key", "summary", "parent_key"],
        },
    },
    {
        "type": "custom",
        "name": "jira_transition_issue",
        "description": "Move a Jira issue to a new workflow status (e.g. 'Done', 'In Progress').",
        "input_schema": {
            "type": "object",
            "properties": {
                "issue_key": {"type": "string"},
                "transition_name": {"type": "string"},
            },
            "required": ["issue_key", "transition_name"],
        },
    },
]

_TOOL_NAMES = {t["name"] for t in JIRA_TOOL_DEFINITIONS}


def is_jira_tool(name: str) -> bool:
    return name in _TOOL_NAMES


def execute_tool(name: str, tool_input: Dict[str, Any], jira: JiraService) -> str:
    """Executes one custom tool call and returns a JSON string result.

    Never raises: any failure is captured and returned as {"error": "..."} so
    the agent can see what went wrong and decide how to proceed or report it.
    """
    try:
        if name == "jira_ensure_project":
            result = jira.ensure_project(tool_input["project_key"], tool_input["project_name"])
        elif name == "jira_create_epic":
            key = jira.create_epic(tool_input["project_key"], tool_input["name"], tool_input["summary"])
            result = {"key": key}
        elif name == "jira_create_story":
            key = jira.create_story(
                project_key=tool_input["project_key"],
                summary=tool_input["summary"],
                description=tool_input["description"],
                epic_key=tool_input.get("epic_key"),
                story_points=tool_input.get("story_points"),
                assignee_name=tool_input.get("assignee_name"),
                assignee_role=tool_input.get("assignee_role"),
            )
            result = {"key": key}
        elif name == "jira_create_subtask":
            key = jira.create_subtask(
                project_key=tool_input["project_key"],
                summary=tool_input["summary"],
                parent_key=tool_input["parent_key"],
                assignee_name=tool_input.get("assignee_name"),
            )
            result = {"key": key}
        elif name == "jira_transition_issue":
            success = jira.transition_issue(tool_input["issue_key"], tool_input["transition_name"])
            result = {"success": success}
        else:
            result = {"error": f"Unknown tool: {name}"}
    except JiraServiceError as exc:
        logger.warning("Jira tool '%s' failed: %s", name, exc)
        result = {"error": str(exc)}
    except KeyError as exc:
        logger.warning("Jira tool '%s' missing required input %s", name, exc)
        result = {"error": f"Missing required input: {exc}"}
    except Exception as exc:  # noqa: BLE001 - never let a tool call crash the session loop
        logger.exception("Unexpected error executing tool '%s'", name)
        result = {"error": f"Unexpected error: {exc}"}

    return json.dumps(result)
