"""Drives Managed Agent sessions: creation, event-stream draining, custom tool
dispatch, and session-output retrieval.

Design notes:
- The agent has Jira tool *schemas* from its very first turn (see
  cma/agent_setup.py), but whether a Jira tool call is actually allowed to
  execute is gated deterministically here in the dispatcher (`allow_jira`),
  based on whether the manager has approved yet — not left to the model's own
  judgment and not implemented via a mid-session tool grant. Live testing
  showed that adding Jira tools to an already-running session via
  `sessions.update()` updates the session's declared config correctly, but the
  model does not reliably call the newly-added tools on the next turn — it
  can just re-emit the prior turn's text instead. Keeping the tools visible
  the whole time (so the model is comfortable calling them once told to) while
  enforcing the actual approval gate in our own code is far more reliable.
- After the sync turn, we verify at least one real Jira tool call happened
  (`_jira_tool_calls_in`). If the agent's turn produced none, we retry once
  with a more forceful nudge before giving up — this catches exactly the
  failure mode above instead of silently reporting success.
- The drain loop replays event history before tailing the live stream (the
  documented "consolidation pattern") so a fast turn that completes before we
  open the stream is never silently missed. On any session with a PRIOR
  completed turn, naively doing this breaks: `events.list()` returns the
  session's entire history, so the *first* terminal `session.status_idle`
  encountered is always the end of the previous turn, not the new one drain
  is supposed to wait for. Live testing showed this causes drain_session to
  return immediately with stale, already-consumed events — including never
  dispatching a brand new `agent.custom_tool_use` event that appears later in
  that same history, leaving the session stuck forever waiting on a tool
  result nobody ever sent. `drain_session` therefore takes `after_event_id`:
  the id of the message that kicked off the turn being drained. Every event
  up to and including that marker is skipped entirely (not dispatched, not
  checked for terminality) — only events after it can end the drain or get
  routed to `on_custom_tool_use`. `send_user_message` returns the id of the
  event it just created for exactly this purpose.
"""
import json
import logging
import time
from pathlib import Path
from typing import Any, Callable, List, Optional

from anthropic import Anthropic

from cma.tools import execute_tool, is_jira_tool
from integrations.jira_service import JiraService

logger = logging.getLogger(__name__)

ToolCallback = Callable[[str, dict], str]

_MAX_STREAM_RECONNECTS = 10


class SessionError(RuntimeError):
    pass


class SyncIncompleteError(RuntimeError):
    """Raised when a Turn 2 sync turn completes without the agent actually
    calling any Jira tool — i.e. nothing was written to Jira despite manager
    approval, even after one forceful retry."""


def _is_terminal(event: Any) -> bool:
    if event.type == "session.status_terminated":
        return True
    if event.type == "session.status_idle":
        stop_reason = getattr(event, "stop_reason", None)
        return getattr(stop_reason, "type", None) != "requires_action"
    return False


def _default_tool_dispatch(jira: Optional[JiraService], allow_jira: bool) -> ToolCallback:
    def _dispatch(name: str, tool_input: dict) -> str:
        if is_jira_tool(name):
            if not allow_jira:
                return json.dumps({
                    "error": (
                        "Jira tools are locked until the manager explicitly approves the plan in Slack. "
                        "Do not call this tool yet — finish Turn 1 and ask for approval instead."
                    )
                })
            if jira is None:
                return json.dumps({"error": "Jira is not configured on this deployment."})
            return execute_tool(name, tool_input, jira)
        return json.dumps({"error": f"No handler registered for tool '{name}'."})

    return _dispatch


def _jira_tool_calls_in(events: List[Any]) -> List[Any]:
    return [e for e in events if e.type == "agent.custom_tool_use" and is_jira_tool(e.name)]


def drain_session(
    client: Anthropic,
    session_id: str,
    on_custom_tool_use: Optional[ToolCallback] = None,
    after_event_id: Optional[str] = None,
) -> List[Any]:
    """Streams a session to a genuinely terminal state, auto-answering any
    `agent.custom_tool_use` events via `on_custom_tool_use`. Returns every
    NEW event observed (i.e. after `after_event_id`, if given), in arrival
    order, deduplicated.

    `after_event_id` should be the id of the message that started the turn
    being drained (see `send_user_message`). Every event up to and including
    it is skipped for both terminal-state detection and tool dispatch — this
    is what stops a stale terminal event, or an already-resolved tool call,
    from a PREVIOUS turn being mistaken for part of the new one. If omitted,
    every event is treated as new from the start (fine for a brand new
    session with no prior turns).
    """
    seen_ids = set()
    new_events: List[Any] = []
    active = after_event_id is None

    def record(event: Any) -> bool:
        event_id = getattr(event, "id", None)
        if event_id:
            if event_id in seen_ids:
                return False
            seen_ids.add(event_id)
        if active:
            new_events.append(event)
        return True

    def handle_tool_use(event: Any) -> None:
        if event.type != "agent.custom_tool_use" or on_custom_tool_use is None:
            return
        result_text = on_custom_tool_use(event.name, event.input)
        client.beta.sessions.events.send(
            session_id=session_id,
            events=[{
                "type": "user.custom_tool_result",
                "custom_tool_use_id": event.id,
                "content": [{"type": "text", "text": result_text}],
            }],
        )

    def process(event: Any) -> bool:
        """Records/dispatches `event` if we're past the marker. Returns True
        when draining should stop (a genuinely new terminal state)."""
        nonlocal active
        first_seen = record(event)
        if not active:
            if getattr(event, "id", None) == after_event_id:
                active = True
            return False
        if first_seen:
            handle_tool_use(event)
        return _is_terminal(event)

    # 1. Replay history first — covers the race where the turn already
    #    finished before we open the live stream.
    for event in client.beta.sessions.events.list(session_id=session_id):
        if process(event):
            return new_events

    # 2. Tail the live stream, reconnecting a bounded number of times if the
    #    connection drops before a terminal event is observed.
    for _attempt in range(_MAX_STREAM_RECONNECTS):
        reached_terminal = False
        with client.beta.sessions.events.stream(session_id=session_id) as stream:
            for event in stream:
                if process(event):
                    reached_terminal = True
                    break
        if reached_terminal:
            return new_events

        session = client.beta.sessions.retrieve(session_id)
        if session.status == "terminated":
            return new_events
        # Otherwise the stream dropped transiently; loop and reconnect.

    raise SessionError(
        f"Session {session_id} did not reach a terminal state after "
        f"{_MAX_STREAM_RECONNECTS} stream reconnect attempts."
    )


def extract_final_text(events: List[Any]) -> str:
    """Returns the text of the last agent.message in the event list, or a descriptive error if the turn failed."""
    for event in reversed(events):
        if event.type == "agent.message":
            texts = [block.text for block in event.content if getattr(block, "type", None) == "text"]
            if texts:
                return "\n".join(texts)

    for event in reversed(events):
        if event.type == "session.error":
            err_obj = getattr(event, "error", None)
            msg = getattr(err_obj, "message", None) or "Session failed unexpectedly."
            return f"⚠️ **Managed Agent Error**: {msg} Please try again in a few moments."

    return ""


def create_session(
    client: Anthropic,
    agent_id: str,
    environment_id: str,
    title: str = "GWC PM Agent — project session",
) -> Any:
    """Creates a session, registered idle with no work started yet.

    Note: the installed `anthropic` SDK's `sessions.create()` does not accept
    an `initial_events` parameter, so the kickoff message must be sent as a
    separate `events.send()` call right after creation (see
    `run_project_turn`) rather than bundled into the create request.
    `drain_session()` replays event history before tailing the live stream,
    so that two-step sequence cannot lose events even without true
    stream-before-send concurrency.
    """
    return client.beta.sessions.create(
        agent={"type": "agent", "id": agent_id},
        environment_id=environment_id,
        title=title,
    )


def send_user_message(client: Anthropic, session_id: str, text: str) -> str:
    """Sends a user message and returns its event id, to be passed as
    `drain_session`'s `after_event_id` so the drain can't mistake a stale
    terminal event from an earlier turn for this one's completion."""
    response = client.beta.sessions.events.send(
        session_id=session_id,
        events=[{"type": "user.message", "content": [{"type": "text", "text": text}]}],
    )
    return response.data[0].id


def run_analysis_turn(
    client: Anthropic,
    agent_id: str,
    environment_id: str,
    kickoff_text: str,
    jira: Optional[JiraService] = None,
) -> Any:
    """Turn 1: Analysis & Sprint Planning. Jira tool schemas are present on the
    session but locked — the dispatcher rejects any Jira tool call this turn."""
    session = create_session(client, agent_id, environment_id)
    marker = send_user_message(client, session.id, kickoff_text)
    events = drain_session(
        client, session.id,
        on_custom_tool_use=_default_tool_dispatch(jira, allow_jira=False),
        after_event_id=marker,
    )
    session.final_text = extract_final_text(events)  # type: ignore[attr-defined]
    return session


def run_sync_turn(
    client: Anthropic,
    session_id: str,
    confirmed_key_reply: str,
    jira: Optional[JiraService],
) -> str:
    """Turn 2: Sends the manager-approved sync prompt with Jira tools unlocked.

    If the agent's turn doesn't actually call any Jira tool (the failure mode
    found via live testing — the model re-emitting the Turn 1 plan instead of
    acting), retries once with a more forceful nudge. If that also produces no
    Jira tool call, raises SyncIncompleteError instead of returning the
    agent's (non-)answer as if it were a completion report.
    """
    prompt_text = (
        f"The manager has approved the plan (reply: '{confirmed_key_reply}'). Jira tools are now UNLOCKED. "
        "Proceed IMMEDIATELY to Turn 2: your very first action must be an actual tool call to `jira_ensure_project` "
        "to verify/create the Jira board, then call `jira_create_epic`, `jira_create_story`, and `jira_create_subtask` "
        "to populate all Epics, User Stories, and Sub-tasks in Jira now. Do not restate the plan, the backlog table, "
        "or the permission request — approval has already been given. When finished, output ONLY the final "
        "Sync Completion Report."
    )
    marker = send_user_message(client, session_id, prompt_text)
    events = drain_session(
        client, session_id,
        on_custom_tool_use=_default_tool_dispatch(jira, allow_jira=True),
        after_event_id=marker,
    )

    if not _jira_tool_calls_in(events):
        logger.warning(
            "Sync turn for session %s produced no Jira tool calls; retrying once with a stronger nudge.",
            session_id,
        )
        retry_prompt = (
            "You did NOT call any Jira tool in your last turn. That is required now. Call `jira_ensure_project` "
            "immediately as a real tool call — not text — then create the Epics/Stories/Sub-tasks. Do not repeat "
            "the plan summary and do not ask for approval again; it has already been granted."
        )
        retry_marker = send_user_message(client, session_id, retry_prompt)
        events = drain_session(
            client, session_id,
            on_custom_tool_use=_default_tool_dispatch(jira, allow_jira=True),
            after_event_id=retry_marker,
        )
        if not _jira_tool_calls_in(events):
            raise SyncIncompleteError(
                "The agent did not call any Jira tool after two attempts — no Jira project or issues were created."
            )

    return extract_final_text(events)


def run_followup_turn(
    client: Anthropic,
    session_id: str,
    message_text: str,
    jira: Optional[JiraService],
) -> str:
    """Sends a follow-up message to an existing (already-synced) session and
    returns the final text response. Jira tools are unlocked here since this
    is only reached after a successful sync."""
    marker = send_user_message(client, session_id, message_text)
    events = drain_session(
        client, session_id,
        on_custom_tool_use=_default_tool_dispatch(jira, allow_jira=True),
        after_event_id=marker,
    )
    return extract_final_text(events)


def download_session_outputs(client: Anthropic, session_id: str, target_dir: Path) -> List[Path]:
    """Downloads every file the agent wrote to /mnt/session/outputs/ during
    the session. Retries briefly to absorb the documented indexing lag."""
    target_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []

    for attempt in range(3):
        files = list(client.beta.files.list(scope_id=session_id, betas=["managed-agents-2026-04-01"]))
        if files:
            for f in files:
                content = client.beta.files.download(f.id)
                dest = target_dir / f.filename
                content.write_to_file(str(dest))
                written.append(dest)
            return written
        if attempt < 2:
            time.sleep(2)

    logger.info("No session output files found for session %s", session_id)
    return written
