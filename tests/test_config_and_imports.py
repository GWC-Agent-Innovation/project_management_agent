"""Sanity tests that run with no Anthropic/Slack/Jira credentials.

These verify config validation, helper logic, and that every module in the
project imports cleanly. They do NOT exercise any live API call — that
requires real credentials and is out of scope for this suite.

Run with:  python -m unittest discover tests
"""
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config  # noqa: E402
import utils  # noqa: E402
from cma import tools as cma_tools  # noqa: E402
from cma import agent_setup  # noqa: E402
from cma import session_manager  # noqa: E402
from integrations import slack_listener  # noqa: E402


class ImportSanityTests(unittest.TestCase):
    def test_all_modules_import(self):
        import logging_config  # noqa: F401
        import team_roster  # noqa: F401
        from cma import session_manager  # noqa: F401
        from integrations import jira_service  # noqa: F401
        from integrations import attachment_extractor  # noqa: F401
        from integrations import slack_listener  # noqa: F401


class ConfigValidationTests(unittest.TestCase):
    def setUp(self):
        # Isolate from any real .env / env vars on the machine running the tests.
        self._env_backup = dict(os.environ)
        for key in list(os.environ):
            if key.startswith(("SLACK_", "ANTHROPIC_", "JIRA_", "CMA_", "OUTPUT_", "STATE_")):
                del os.environ[key]

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env_backup)

    @mock.patch("config._load_env", lambda: None)
    def test_setup_config_requires_anthropic_key(self):
        with self.assertRaises(config.ConfigError):
            config.load_setup_config()

    @mock.patch("config._load_env", lambda: None)
    def test_setup_config_rejects_placeholder_key(self):
        os.environ["ANTHROPIC_API_KEY"] = "sk-ant-replace-with-your-key"
        with self.assertRaises(config.ConfigError):
            config.load_setup_config()

    @mock.patch("config._load_env", lambda: None)
    def test_setup_config_accepts_real_looking_key(self):
        os.environ["ANTHROPIC_API_KEY"] = "sk-ant-abc123"
        cfg = config.load_setup_config()
        self.assertEqual(cfg.api_key, "sk-ant-abc123")
        self.assertEqual(cfg.model, "claude-sonnet-5")

    @mock.patch("config._load_env", lambda: None)
    def test_runtime_config_reports_all_missing_vars(self):
        with self.assertRaises(config.ConfigError) as ctx:
            config.load_runtime_config()
        message = str(ctx.exception)
        for expected in ("SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "SLACK_CHANNEL_ID", "ANTHROPIC_API_KEY"):
            self.assertIn(expected, message)

    @mock.patch("config._load_env", lambda: None)
    def test_runtime_config_succeeds_without_jira(self):
        os.environ.update({
            "SLACK_BOT_TOKEN": "xoxb-real-token",
            "SLACK_APP_TOKEN": "xapp-real-token",
            "SLACK_CHANNEL_ID": "C012345678",
            "ANTHROPIC_API_KEY": "sk-ant-abc123",
            "CMA_AGENT_ID": "agent_abc123",
            "CMA_ENVIRONMENT_ID": "env_abc123",
        })
        cfg = config.load_runtime_config()
        self.assertIsNone(cfg.jira)
        self.assertEqual(cfg.slack.channel_id, "C012345678")

    @mock.patch("config._load_env", lambda: None)
    def test_runtime_config_picks_up_jira_when_fully_set(self):
        os.environ.update({
            "SLACK_BOT_TOKEN": "xoxb-real-token",
            "SLACK_APP_TOKEN": "xapp-real-token",
            "SLACK_CHANNEL_ID": "C012345678",
            "ANTHROPIC_API_KEY": "sk-ant-abc123",
            "CMA_AGENT_ID": "agent_abc123",
            "CMA_ENVIRONMENT_ID": "env_abc123",
            "JIRA_URL": "https://acme.atlassian.net",
            "JIRA_EMAIL": "pm@acme.com",
            "JIRA_API_TOKEN": "real-token-value",
        })
        cfg = config.load_runtime_config()
        self.assertIsNotNone(cfg.jira)
        self.assertEqual(cfg.jira.url, "https://acme.atlassian.net")


class UtilsTests(unittest.TestCase):
    def test_clean_project_filename_from_h1(self):
        md = "# Smart Gym Tracker\n\nSome overview text."
        self.assertEqual(utils.clean_project_filename(md), "Smart_Gym_Tracker.md")

    def test_clean_project_filename_falls_back(self):
        self.assertEqual(utils.clean_project_filename("no headers here"), "project_details.md")

    def test_extract_first_project_key_found(self):
        text = "Created KAN-12 and KAN-13 under the Epic."
        self.assertEqual(utils.extract_first_project_key(text), "KAN")

    def test_extract_first_project_key_missing(self):
        self.assertIsNone(utils.extract_first_project_key("no issue keys here"))


class ToolDefinitionTests(unittest.TestCase):
    def test_five_jira_tools_registered(self):
        names = {t["name"] for t in cma_tools.JIRA_TOOL_DEFINITIONS}
        self.assertEqual(names, {
            "jira_ensure_project",
            "jira_create_epic",
            "jira_create_story",
            "jira_create_subtask",
            "jira_transition_issue",
        })

    def test_every_tool_has_valid_schema_shape(self):
        for tool in cma_tools.JIRA_TOOL_DEFINITIONS:
            self.assertEqual(tool["type"], "custom")
            self.assertIn("description", tool)
            schema = tool["input_schema"]
            self.assertEqual(schema["type"], "object")
            for required_field in schema.get("required", []):
                self.assertIn(required_field, schema["properties"])

    def test_is_jira_tool(self):
        self.assertTrue(cma_tools.is_jira_tool("jira_create_epic"))
        self.assertFalse(cma_tools.is_jira_tool("bash"))


class ToolDispatchGatingTests(unittest.TestCase):
    """Covers the client-side approval gate: Jira tool calls must be rejected
    before approval regardless of what the model attempts, and allowed after."""

    def test_jira_call_rejected_when_locked(self):
        dispatch = session_manager._default_tool_dispatch(jira=None, allow_jira=False)
        result = dispatch("jira_ensure_project", {"project_key": "KAN", "project_name": "x"})
        self.assertIn("locked", result.lower())

    def test_jira_call_allowed_but_reports_unconfigured_without_jira_service(self):
        dispatch = session_manager._default_tool_dispatch(jira=None, allow_jira=True)
        result = dispatch("jira_ensure_project", {"project_key": "KAN", "project_name": "x"})
        self.assertIn("not configured", result.lower())

    def test_non_jira_tool_unaffected_by_lock(self):
        dispatch = session_manager._default_tool_dispatch(jira=None, allow_jira=False)
        result = dispatch("some_other_tool", {})
        self.assertIn("No handler registered", result)

    def test_jira_tool_calls_in_filters_by_event_type_and_name(self):
        class FakeEvent:
            def __init__(self, type_, name=None):
                self.type = type_
                self.name = name

        events = [
            FakeEvent("agent.message"),
            FakeEvent("agent.custom_tool_use", name="jira_create_epic"),
            FakeEvent("agent.tool_use", name="write"),
            FakeEvent("agent.custom_tool_use", name="not_a_jira_tool"),
        ]
        matches = session_manager._jira_tool_calls_in(events)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].name, "jira_create_epic")


class ApprovalReplyMatchingTests(unittest.TestCase):
    """The strict exact-match-only version of this rejected real approval
    replies like 'yes, approved!' and left the manager stuck re-reading the
    same plan forever -- these lock in the looser matching that fixed it."""

    def _is_approved(self, text):
        return bool(slack_listener._VALID_KEY_RE.match(text) or slack_listener._APPROVAL_RE.match(text))

    def test_natural_language_approvals_accepted(self):
        for text in ["yes", "Yes, approved!", "yes go ahead", "sure", "LGTM", "sounds good", "approved"]:
            with self.subTest(text=text):
                self.assertTrue(self._is_approved(text))

    def test_bare_project_key_accepted(self):
        self.assertTrue(self._is_approved("HMS"))
        self.assertTrue(self._is_approved("kan"))

    def test_unrelated_reply_not_treated_as_approval(self):
        for text in ["can you change sprint 1", "what about the timeline", "not sure yet"]:
            with self.subTest(text=text):
                self.assertFalse(self._is_approved(text))


def _text_msg(event_id, event_type, text=None, **extra):
    kwargs = dict(id=event_id, type=event_type, **extra)
    if text is not None:
        kwargs["content"] = [SimpleNamespace(type="text", text=text)]
    return SimpleNamespace(**kwargs)


class DrainSessionMarkerTests(unittest.TestCase):
    """Regression coverage for the core bug found via live testing:
    events.list() returns a session's ENTIRE history, so without a marker,
    drain_session stops at the first terminal session.status_idle it finds --
    which on any second-or-later turn is always the END of the PREVIOUS turn,
    not the new one. That silently returned stale data and, worse, never
    dispatched a brand new agent.custom_tool_use event sitting later in that
    same history, leaving the session stuck forever waiting on an unresolved
    tool call. after_event_id fixes this by ignoring everything up to and
    including the message that started the turn being drained."""

    def _build_fake_client(self, events, tool_result_calls):
        client = mock.MagicMock()
        client.beta.sessions.events.list.return_value = events

        def fake_send(session_id, events):
            for e in events:
                if e.get("type") == "user.custom_tool_result":
                    tool_result_calls.append(e["custom_tool_use_id"])
            return SimpleNamespace(data=[SimpleNamespace(id="sevt_sent")])

        client.beta.sessions.events.send.side_effect = fake_send
        return client

    def test_stale_prior_turn_terminal_event_is_ignored(self):
        events = [
            _text_msg("e1", "session.status_running"),
            _text_msg("e2", "user.message"),
            _text_msg("e3", "agent.message", text="OLD TURN 1 TEXT"),
            _text_msg("e4", "session.status_idle", stop_reason=SimpleNamespace(type="end_turn")),
            _text_msg("e5", "session.status_running"),
            _text_msg("e6", "user.message"),  # this is the marker for the new turn
            _text_msg(
                "e7", "agent.custom_tool_use",
                name="jira_ensure_project", input={"project_key": "X", "project_name": "Y"},
            ),
            _text_msg("e8", "agent.message", text="NEW TURN 2 TEXT"),
            _text_msg("e9", "session.status_idle", stop_reason=SimpleNamespace(type="end_turn")),
        ]
        tool_result_calls = []
        client = self._build_fake_client(events, tool_result_calls)

        dispatch_calls = []

        def dispatch(name, tool_input):
            dispatch_calls.append((name, tool_input))
            return '{"ok": true}'

        new_events = session_manager.drain_session(
            client, "sess1", on_custom_tool_use=dispatch, after_event_id="e6",
        )

        # Only post-marker events come back -- the stale Turn 1 message and
        # its terminal idle must not appear at all.
        self.assertEqual([e.id for e in new_events], ["e7", "e8", "e9"])

        # The new agent.custom_tool_use event WAS dispatched and resolved --
        # this is the specific thing that silently never happened before the fix.
        self.assertEqual(dispatch_calls, [("jira_ensure_project", {"project_key": "X", "project_name": "Y"})])
        self.assertEqual(tool_result_calls, ["e7"])

        final_text = session_manager.extract_final_text(new_events)
        self.assertEqual(final_text, "NEW TURN 2 TEXT")

    def test_no_marker_behaves_as_before_for_a_brand_new_session(self):
        events = [
            _text_msg("e1", "session.status_running"),
            _text_msg("e2", "user.message"),
            _text_msg("e3", "agent.message", text="TURN 1 TEXT"),
            _text_msg("e4", "session.status_idle", stop_reason=SimpleNamespace(type="end_turn")),
        ]
        client = self._build_fake_client(events, [])
        new_events = session_manager.drain_session(client, "sess1", after_event_id=None)
        self.assertEqual([e.id for e in new_events], ["e1", "e2", "e3", "e4"])
        self.assertEqual(session_manager.extract_final_text(new_events), "TURN 1 TEXT")


class AgentSetupTests(unittest.TestCase):
    def test_system_prompt_assembles_all_three_docs(self):
        prompt = agent_setup.build_system_prompt()
        self.assertIn("Role", prompt)
        self.assertIn("Requirements Analysis Methodology", prompt)
        self.assertIn("Backlog Planning Methodology", prompt)
        self.assertGreater(len(prompt), 1000)

    def test_base_tools_include_jira_schemas_from_the_start(self):
        # Jira tool *schemas* are present on the session from Turn 1 onward so
        # the model reliably knows how to call them once told to -- actually
        # executing one before manager approval is blocked in
        # session_manager.py's dispatcher (allow_jira=False), not by omitting
        # the tool definitions from the session.
        tool_types = {t.get("type") for t in agent_setup.BASE_TOOLS}
        self.assertIn("agent_toolset_20260401", tool_types)
        self.assertIn("custom", tool_types)

        custom_names = {t["name"] for t in agent_setup.BASE_TOOLS if t.get("type") == "custom"}
        jira_names = {t["name"] for t in cma_tools.JIRA_TOOL_DEFINITIONS}
        self.assertEqual(custom_names, jira_names)


if __name__ == "__main__":
    unittest.main()
