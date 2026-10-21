"""Slack Socket Mode listener.

Three event shapes are handled:
  1. A new (non-thread) message in the requirements channel -> run the full
     Managed Agent workflow in one turn: analyze, write the spec, determine
     the Jira key, and sync the whole backlog to Jira — no human confirmation
     step, per the agent's system prompt.
  2. A threaded reply to that message -> forward it as a follow-up message to
     the *same* session (e.g. "also add a story for X", "transition KAN-5 to
     Done") — the agent already has Jira tools, so it can act immediately.
  3. A message in one of the resulting project channels containing a
     completion phrase + issue key (e.g. "KAN-42 is done") -> transition that
     issue to Done directly (no agent call needed — this is a deterministic
     regex match, kept simple and fast on purpose).
"""
import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, Optional

from slack_sdk import WebClient
from slack_sdk.socket_mode.builtin import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse

from anthropic import Anthropic

from cma import session_manager
from config import RuntimeConfig
from integrations import attachment_extractor
from integrations.jira_service import JiraService
import team_roster
from utils import (
    clean_project_filename,
    extract_first_project_key,
    load_json_state,
    save_json_state,
)

logger = logging.getLogger(__name__)

_COMPLETION_RE = re.compile(r"\b(completed|done)\b", re.IGNORECASE)
_ISSUE_KEY_RE = re.compile(r"([A-Z][A-Z0-9]{1,9}-\d+)")
_VALID_KEY_RE = re.compile(r"^[A-Za-z0-9]{2,5}$")
# Natural-language approvals ("yes, approved!", "yes go ahead", "lgtm") in
# addition to a bare project key -- the strict exact-match-only version of
# this caused real approval replies to be rejected and the plan re-asked.
_APPROVAL_RE = re.compile(r"^\s*(yes|yeah|yep|approved?|go\s*ahead|lgtm|sounds good|sure)\b", re.IGNORECASE)


class SlackAgentListener:
    def __init__(
        self,
        config: RuntimeConfig,
        anthropic_client: Anthropic,
        jira: Optional[JiraService],
    ):
        self.config = config
        self.anthropic = anthropic_client
        self.jira = jira
        self.web_client = WebClient(token=config.slack.bot_token)
        self.bot_user_id: Optional[str] = None

        self.state_path = config.state_dir / "active_sessions.json"
        # thread_ts -> {"session_id": str, "channel_created": bool}
        self.threads: Dict[str, Any] = load_json_state(self.state_path)

        self.project_channels_path = config.state_dir / "project_channels.json"
        # set of channel ids created for confirmed projects, persisted as a list
        self.project_channels = set(load_json_state(self.project_channels_path).get("channels", []))

        self.output_dir = Path(__file__).resolve().parent.parent

    # ------------------------------------------------------------------
    # Setup

    def connect(self) -> SocketModeClient:
        auth = self.web_client.auth_test()
        self.bot_user_id = auth["user_id"]
        logger.info("Connected to Slack as bot user %s", self.bot_user_id)

        socket_client = SocketModeClient(app_token=self.config.slack.app_token, web_client=self.web_client)
        socket_client.socket_mode_request_listeners.append(self._on_request)
        return socket_client

    def _save_threads(self) -> None:
        save_json_state(self.state_path, self.threads)

    def _save_project_channels(self) -> None:
        save_json_state(self.project_channels_path, {"channels": sorted(self.project_channels)})

    # ------------------------------------------------------------------
    # Socket Mode dispatch

    def _on_request(self, client: SocketModeClient, request: SocketModeRequest) -> None:
        client.send_socket_mode_response(SocketModeResponse(envelope_id=request.envelope_id))

        if request.type != "events_api":
            return

        event = request.payload.get("event", {})
        if event.get("type") != "message":
            return
        if event.get("subtype") in ("message_deleted", "bot_message"):
            return
        if event.get("user") == self.bot_user_id:
            return

        try:
            self._route_message_event(event)
        except Exception:  # noqa: BLE001 - never let one bad event kill the daemon
            logger.exception("Unhandled error processing Slack event: %s", event)
            self._safe_reply(
                channel=event.get("channel"),
                thread_ts=event.get("thread_ts") or event.get("ts"),
                text="Something went wrong processing that message. Check the daemon logs for details.",
            )

    def _route_message_event(self, event: Dict[str, Any]) -> None:
        channel = event.get("channel")
        thread_ts = event.get("thread_ts")
        text_snippet = (event.get("text") or "")[:60]
        logger.info("Incoming message event: channel=%s, user=%s, thread_ts=%s, snippet=%r", channel, event.get("user"), thread_ts, text_snippet)

        if channel in self.project_channels:
            self._handle_project_channel_message(channel, event)
            return

        if channel == self.config.slack.channel_id:
            if thread_ts and thread_ts in self.threads:
                self._handle_thread_reply(channel, thread_ts, event)
                return
            elif not thread_ts:
                self._handle_new_requirements_message(channel, event)
                return
            else:
                logger.info("Thread reply on untracked thread %s; treating as new requirements message.", thread_ts)
                self._handle_new_requirements_message(channel, event)
                return

        logger.warning("Message received in channel %s, but configured listening channel is %s", channel, self.config.slack.channel_id)

    # ------------------------------------------------------------------
    # Case 3 (checked first): completion message in a project channel

    def _handle_project_channel_message(self, channel: str, event: Dict[str, Any]) -> None:
        text = event.get("text", "")
        if not _COMPLETION_RE.search(text):
            return
        match = _ISSUE_KEY_RE.search(text)
        if not match or self.jira is None:
            return

        issue_key = match.group(1)
        logger.info("Detected completion message for %s in %s", issue_key, channel)
        if self.jira.transition_issue(issue_key, "Done"):
            self._safe_reaction(channel, event.get("ts"), "white_check_mark")

    # ------------------------------------------------------------------
    # Case 1: new requirements message — Turn 1: Analysis & Sprint Planning

    def _handle_new_requirements_message(self, channel: str, event: Dict[str, Any]) -> None:
        ts = event.get("ts")
        user = event.get("user")
        text = (event.get("text") or "").strip()

        self._safe_reaction(channel, ts, "eyes")

        content_parts = []
        if text:
            content_parts.append(text)
        for file_info in event.get("files", []):
            download_url = file_info.get("url_private_download")
            if not download_url:
                continue
            try:
                data = attachment_extractor.download_file(download_url, self.config.slack.bot_token)
                extracted = attachment_extractor.extract_text(
                    file_info.get("name", "unnamed_file"), file_info.get("mimetype", ""), data
                )
                content_parts.append(
                    f"--- ATTACHMENT: {file_info.get('name', 'unnamed_file')} ---\n{extracted}\n--- END ATTACHMENT ---"
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to process attachment on message %s: %s", ts, exc)

        raw_text = "\n\n".join(content_parts).strip()
        if not raw_text:
            logger.info("Message %s had no usable content; ignoring.", ts)
            return

        kickoff_text = self._build_kickoff_text(raw_text)

        try:
            session = session_manager.run_analysis_turn(
                self.anthropic,
                self.config.anthropic.agent_id,
                self.config.anthropic.environment_id,
                kickoff_text,
                self.jira,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Analysis session failed for message %s", ts)
            self._safe_reply(channel, ts, f"Error while processing this request: {exc}")
            return

        self.threads[ts] = {"session_id": session.id, "phase": "awaiting_confirmation"}
        self._save_threads()

        self._save_output_file(session.id, ts)

        final_text = session.final_text or "(the agent returned no text — check the session in the Console)"
        self._safe_reply(channel, ts, final_text)
        self._safe_reaction(channel, ts, "white_check_mark")
        logger.info("Stored session %s for thread %s (awaiting manager approval)", session.id, ts)

    def _build_kickoff_text(self, raw_text: str) -> str:
        roster_block = team_roster.format_roster_for_prompt()
        return (
            "A new project requirement has been posted in Slack. Run Turn 1 (Analysis & Sprint Planning) now: "
            "produce the project specification (and save it to /mnt/session/outputs/project_details.md), "
            "design the Sprint breakdown plan and timeline, determine/propose the Jira project key, "
            "and request permission from the manager in your Slack summary. Do not call any Jira tool yet.\n\n"
            f"--- TEAM ROSTER ---\n{roster_block}\n--- END TEAM ROSTER ---\n\n"
            f"--- RAW SLACK CONTENT ---\n{raw_text}\n--- END RAW SLACK CONTENT ---"
        )

    def _save_output_file(self, session_id: str, thread_ts: str) -> None:
        try:
            written = session_manager.download_session_outputs(self.anthropic, session_id, self.output_dir / "outputs")
            for path in written:
                final_path = self._dedupe_output_filename(path, thread_ts)
                logger.info("Saved session output: %s", final_path)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not download session outputs for %s: %s", session_id, exc)

    def _dedupe_output_filename(self, path: Path, thread_ts: str) -> Path:
        """The agent always writes to the literal path
        /mnt/session/outputs/project_details.md per its system prompt, so
        every downloaded file arrives with the same filename regardless of
        project -- without this, each new project silently overwrites the
        previous one's spec file on disk. Renames using the project's own
        title (extracted from its H1) when possible, falling back to a
        thread-unique name, with a numeric suffix as a last resort."""
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            text = ""

        filename = clean_project_filename(text, default_filename=path.name)
        if filename == "project_details.md":
            filename = f"{thread_ts.replace('.', '_')}_{path.name}"

        dest = path.with_name(filename)
        counter = 1
        while dest.exists() and dest != path:
            stem = filename.rsplit(".", 1)[0]
            dest = path.with_name(f"{stem}_{counter}.md")
            counter += 1

        if dest != path:
            path.replace(dest)
        return dest

    # ------------------------------------------------------------------
    # Case 2: thread reply — Manager Approval / Turn 2 Sync or Follow-up

    def _handle_thread_reply(self, channel: str, thread_ts: str, event: Dict[str, Any]) -> None:
        state = self.threads[thread_ts]
        reply_text = (event.get("text") or "").strip()
        user = event.get("user")
        ts = event.get("ts")
        if not reply_text:
            return

        self._safe_reaction(channel, ts, "eyes")

        session_id = state["session_id"]
        phase = state.get("phase", "awaiting_confirmation")

        if phase == "awaiting_confirmation":
            if not (_VALID_KEY_RE.match(reply_text) or _APPROVAL_RE.match(reply_text)):
                self._safe_reply(
                    channel, thread_ts,
                    "Please reply with `yes` to approve the proposed plan, or enter a 2-5 character Jira project key (e.g. `HMS`).",
                )
                return

            self._safe_reaction(channel, ts, "white_check_mark")
            self._safe_reply(
                channel, thread_ts,
                "⏳ **Plan Approved!** Creating Jira project board and syncing Epics/Stories/Sub-tasks... Please hold on a moment.",
            )

            try:
                final_text = session_manager.run_sync_turn(self.anthropic, session_id, reply_text, self.jira)
            except session_manager.SyncIncompleteError as exc:
                logger.error("Jira sync turn did not create anything for thread %s: %s", thread_ts, exc)
                self._safe_reply(
                    channel, thread_ts,
                    f"⚠️ {exc} Nothing was written to Jira. Reply `yes` again to retry, or check the daemon logs.",
                )
                return
            except Exception as exc:  # noqa: BLE001
                logger.exception("Jira sync turn failed for thread %s", thread_ts)
                self._safe_reply(channel, thread_ts, f"Jira sync failed: {exc}")
                return

            state["phase"] = "synced"
            self._save_threads()

            self._safe_reply(channel, thread_ts, final_text or "(Jira sync finished but returned no text)")

            project_key = extract_first_project_key(final_text)
            # Fall back: if the agent's response has no issue key like HMS-1,
            # use the manager's own reply as the project key (they typed it or said "yes").
            # If they said "yes"/approval phrase, try to pull the key from the agent's
            # earlier turn-1 response (not available here), so we skip channel creation
            # only when we truly have no key at all.
            if not project_key and _VALID_KEY_RE.match(reply_text.strip()):
                project_key = reply_text.strip().upper()
                logger.info("No issue key found in agent response; using manager's reply as project key: %s", project_key)
            if project_key:
                self._create_project_channel(channel, thread_ts, user, project_key)
            else:
                logger.warning("Could not determine project key from agent response or manager reply — skipping channel creation.")
        else:
            try:
                final_text = session_manager.run_followup_turn(self.anthropic, session_id, reply_text, self.jira)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Follow-up turn failed for thread %s", thread_ts)
                self._safe_reply(channel, thread_ts, f"Follow-up failed: {exc}")
                return

            self._safe_reply(channel, thread_ts, final_text or "(the agent returned no text for that follow-up)")
            self._safe_reaction(channel, ts, "white_check_mark")

    def _create_project_channel(self, channel: str, thread_ts: str, user: Optional[str], project_key: str) -> None:
        slug = re.sub(r"[^a-z0-9-]", "", project_key.lower())[:40]
        channel_name = f"proj-{slug}" if slug else "proj-new"
        try:
            created = self.web_client.conversations_create(name=channel_name)
            project_channel_id = created["channel"]["id"]
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not create project channel '%s': %s", channel_name, exc)
            return

        for member in filter(None, (user, self.bot_user_id)):
            try:
                self.web_client.conversations_invite(channel=project_channel_id, users=[member])
            except Exception as exc:  # noqa: BLE001
                logger.warning("Could not invite %s to %s: %s", member, channel_name, exc)

        self.project_channels.add(project_channel_id)
        self._save_project_channels()

        jira_link = self.jira.project_url(project_key) if self.jira else "(Jira not configured)"
        self._safe_reply(
            project_channel_id, None,
            f"Welcome to #{channel_name}!\n\n"
            f"Jira board: {project_key} — {jira_link}\n\n"
            "I'm monitoring this channel: when someone posts a message like "
            f"\"{project_key}-12 done\", I'll move that ticket to Done automatically.",
        )
        self._safe_reply(channel, thread_ts, f"Created project channel <#{project_channel_id}> and invited you.")

    # ------------------------------------------------------------------
    # Slack helpers

    def _safe_reply(self, channel: Optional[str], thread_ts: Optional[str], text: str) -> None:
        if not channel:
            return
        try:
            kwargs = {"channel": channel, "text": text}
            if thread_ts:
                kwargs["thread_ts"] = thread_ts
            self.web_client.chat_postMessage(**kwargs)
        except Exception as exc:  # noqa: BLE001
            logger.error("Could not post message to %s: %s", channel, exc)

    def _safe_reaction(self, channel: Optional[str], ts: Optional[str], name: str) -> None:
        if not channel or not ts:
            return
        try:
            self.web_client.reactions_add(channel=channel, timestamp=ts, name=name)
        except Exception as exc:  # noqa: BLE001
            logger.debug("Could not add reaction '%s' to %s/%s: %s", name, channel, ts, exc)


def run_forever(config: RuntimeConfig, anthropic_client: Anthropic, jira: Optional[JiraService]) -> None:
    listener = SlackAgentListener(config, anthropic_client, jira)
    socket_client = listener.connect()
    socket_client.connect()
    logger.info("Listening for Slack events on channel %s. Press Ctrl+C to exit.", config.slack.channel_id)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutdown signal received.")
