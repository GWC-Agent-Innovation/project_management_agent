"""Thin, defensive wrapper around the `jira` Python SDK.

This is intentionally kept as plain client-side code (not an MCP server) so
that the Jira API token never has to leave our own process — it is never
passed into the Managed Agent's sandbox. The agent only ever sees the tool
schemas in cma/tools.py and their string results.
"""
import json
import logging
from typing import Any, Dict, Optional

from jira import JIRA

logger = logging.getLogger(__name__)

# Project templates to try, in order, when creating a new Jira Cloud project.
# The `jira` library's own create_project() defaults to "gh-simplified-basic"
# when no template is given; we try the Kanban-specific template first since
# that's what this project actually wants, falling back to basic if the site
# doesn't offer it.
_PROJECT_TEMPLATE_KEYS = (
    "com.pyxis.greenhopper.jira:gh-simplified-kanban-classic",
    "com.pyxis.greenhopper.jira:gh-simplified-basic",
)


class JiraServiceError(RuntimeError):
    """Raised for any Jira operation failure, with a message safe to show the agent/user."""


class JiraService:
    def __init__(self, url: str, email: str, api_token: str):
        try:
            self.jira = JIRA(server=url, basic_auth=(email, api_token))
        except Exception as exc:  # noqa: BLE001 - surface as our own error type
            raise JiraServiceError(f"Could not connect to Jira at {url}: {exc}") from exc

        self.url = url.rstrip("/")
        self._story_points_field = self._discover_story_points_field()
        self._subtask_type_cache: Dict[str, str] = {}

    def _discover_story_points_field(self) -> Optional[str]:
        try:
            for field in self.jira.fields():
                if "story point" in field["name"].lower():
                    logger.info("Discovered Story Points field: %s (%s)", field["id"], field["name"])
                    return field["id"]
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not discover Story Points custom field: %s", exc)
        return None

    def _discover_subtask_type(self, project_key: str) -> str:
        if project_key in self._subtask_type_cache:
            return self._subtask_type_cache[project_key]
        subtask_name = "Sub-task"
        try:
            project = self.jira.project(project_key)
            for issue_type in project.issueTypes:
                if "sub-task" in issue_type.name.lower() or "subtask" in issue_type.name.lower():
                    subtask_name = issue_type.name
                    break
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not discover sub-task issue type for %s: %s", project_key, exc)
        self._subtask_type_cache[project_key] = subtask_name
        return subtask_name

    def ensure_project(self, project_key: str, project_name: str) -> Dict[str, Any]:
        project_key = project_key.strip().upper()
        try:
            self.jira.project(project_key)
            return {"project_key": project_key, "existed": True, "created": False, "url": self.project_url(project_key)}
        except Exception:
            pass

        last_error: Optional[Exception] = None
        for template_key in _PROJECT_TEMPLATE_KEYS:
            try:
                self._create_project_direct(project_key, project_name, template_key)
                return {"project_key": project_key, "existed": False, "created": True, "url": self.project_url(project_key)}
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.warning("Project creation with template '%s' failed for '%s': %s", template_key, project_key, exc)

        raise JiraServiceError(
            f"Project '{project_key}' does not exist and could not be created automatically "
            f"(insufficient permissions, or the key is already taken by a non-software project). "
            f"Create a Software (Kanban/Scrum) project with key '{project_key}' in the Jira UI, "
            f"or choose a different existing key. Details: {last_error}"
        ) from last_error

    def _create_project_direct(self, project_key: str, project_name: str, template_key: str) -> None:
        """Creates a project via a raw REST call instead of the `jira` library's
        `create_project()` helper, for two reasons found via direct testing
        against a real Jira Cloud free-tier site:

        1. That helper raises RuntimeError("Unable to identify valid
           issueSecurityScheme") whenever the site has zero issue security
           schemes configured — normal for most modern team-managed Jira Cloud
           sites, and not actually required by the API (the field is optional
           in the request payload, so we simply never send it).
        2. Explicitly assigning a `permissionScheme` on project creation fails
           on the Jira Cloud free plan with a 500 ("Changing permission
           schemes is not allowed on the Jira free plan.") — even though the
           project creation itself succeeds if `permissionScheme` is omitted
           entirely and Jira is left to apply its own default. So this method
           never sends `permissionScheme` either.
        """
        lead_account_id = self.jira.myself()["accountId"]

        payload = {
            "name": project_name,
            "key": project_key,
            "projectTypeKey": "software",
            "projectTemplateKey": template_key,
            "leadAccountId": lead_account_id,
            "assigneeType": "PROJECT_LEAD",
            "description": "",
            "notificationScheme": 10000,
            "url": "",
        }
        response = self.jira._session.post(self.jira._get_url("project"), data=json.dumps(payload))
        response.raise_for_status()

    def create_epic(self, project_key: str, name: str, summary: str) -> str:
        try:
            issue = self.jira.create_issue(fields={
                "project": {"key": project_key.strip().upper()},
                "summary": f"Epic: {name}",
                "description": summary,
                "issuetype": {"name": "Epic"},
            })
            return issue.key
        except Exception as exc:  # noqa: BLE001
            raise JiraServiceError(f"Failed to create Epic '{name}': {exc}") from exc

    def create_story(
        self,
        project_key: str,
        summary: str,
        description: str,
        epic_key: Optional[str],
        story_points: Optional[float],
        assignee_name: Optional[str] = None,
        assignee_role: Optional[str] = None,
    ) -> str:
        if assignee_name:
            summary = f"[{assignee_name}] {summary}"
            meta = (
                f"Assignee: {assignee_name} ({assignee_role or 'Developer'})\n"
                f"Story Points: {story_points or 0}\n"
                f"{'-' * 40}\n\n"
            )
            description = meta + (description or "")

        fields: Dict[str, Any] = {
            "project": {"key": project_key.strip().upper()},
            "summary": summary,
            "description": description,
            "issuetype": {"name": "Story"},
        }
        if epic_key:
            fields["parent"] = {"key": epic_key}

        try:
            issue = self.jira.create_issue(fields=fields)
        except Exception as exc:  # noqa: BLE001
            raise JiraServiceError(f"Failed to create Story '{summary}': {exc}") from exc

        if self._story_points_field and story_points:
            try:
                issue.update(fields={self._story_points_field: float(story_points)})
            except Exception as exc:  # noqa: BLE001
                logger.warning("Could not set story points on %s: %s", issue.key, exc)

        return issue.key

    def create_subtask(
        self,
        project_key: str,
        summary: str,
        parent_key: str,
        assignee_name: Optional[str] = None,
    ) -> str:
        project_key = project_key.strip().upper()
        if assignee_name:
            summary = f"[{assignee_name}] {summary}"

        try:
            issue = self.jira.create_issue(fields={
                "project": {"key": project_key},
                "summary": summary,
                "issuetype": {"name": self._discover_subtask_type(project_key)},
                "parent": {"key": parent_key},
            })
            return issue.key
        except Exception as exc:  # noqa: BLE001
            raise JiraServiceError(
                f"Failed to create Sub-task '{summary}' under {parent_key}: {exc}"
            ) from exc

    def transition_issue(self, issue_key: str, transition_name: str = "Done") -> bool:
        try:
            issue = self.jira.issue(issue_key)
            transitions = self.jira.transitions(issue)
            transition_id = next(
                (t["id"] for t in transitions if t["name"].lower() == transition_name.lower()),
                None,
            )
            if transition_id:
                self.jira.transition_issue(issue, transition_id)
            else:
                self.jira.transition_issue(issue, transition_name)
            return True
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to transition %s to '%s': %s", issue_key, transition_name, exc)
            return False

    def issue_url(self, issue_key: str) -> str:
        return f"{self.url}/browse/{issue_key}"

    def project_url(self, project_key: str) -> str:
        return f"{self.url}/projects/{project_key}"
