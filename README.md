# GWC Project Management Agent — Claude Managed Agents Edition

A Slack-driven project management agent that analyzes raw requirements, plans an Agile backlog, and syncs it to Jira — built on **Claude Managed Agents** instead of raw LLM completions. This is the CMA-based successor to the original Groq-based prototype at `Project management groq`.

## What's different from the Groq version

| | Groq prototype | This project (Claude Managed Agents) |
|---|---|---|
| LLM orchestration | Two separate stateless completion calls (analyze, then plan) | One persistent **Managed Agent session** per project that does analysis, backlog planning, and Jira sync autonomously in a single turn |
| Jira sync | Orchestrator code decided when to call Jira, via a hand-rolled JSON state file (`pending_sprints.json`) and a manual "reply with the project key" step | The agent has full authority (per its system prompt) to determine/generate the Jira key and sync the whole backlog itself — no human confirmation step |
| Output file | Written by the orchestrator after parsing the LLM's raw text | Written by the agent itself, inside its sandbox, via the built-in `write` tool, then downloaded via the Files API |
| Reusable instructions | Duplicated inline in two big prompt strings | Two versioned methodology docs (`cma/prompts/requirements_analysis.md`, `backlog_planning.md`) folded into one agent system prompt |
| Session state | Re-derived from scratch on every run | A real conversation the agent can be resumed on directly — thread replies become follow-up instructions to the same session (`events.send`) |
| Team roster | Regenerated from JSON on every prompt | Same, but passed as session context rather than baked into a static prompt — no agent redeploy needed when the team changes |
| Model | Groq `llama-3.3-70b-versatile` | Claude Sonnet 5 (`claude-sonnet-5`) |

The "simulated developer chat" feature from the prototype (`simulator.py`) was intentionally **not** carried over — in the original it was imported but never actually invoked, so it wasn't a working feature to replicate. The completion-detection behavior it fed (`"KAN-42 done"` → auto-transition to Done in Jira) *is* kept, as plain deterministic regex + a direct Jira call — no agent involved, on purpose, since it doesn't need one.

## Architecture

```
Slack (Socket Mode)                     Claude Managed Agents                    Jira Cloud
────────────────────                    ──────────────────────                   ──────────
New message in                          Session created, kickoff message sent.
#requirements channel        ────────►  Agent has Jira tools from turn one.
                                         Analyzes requirements, writes
                                         project_details.md to its sandbox,
                                         drafts the backlog, determines or
                                         generates the Jira key, and calls
                                         jira_ensure_project / _create_epic /       Epics, Stories,
                                         _create_story / _create_subtask  ───────►  Sub-tasks created
                                         as needed — all in this one turn.
Summary + new #proj-xxx       ◄────────
channel posted

Thread reply                 ────────►  Forwarded as a follow-up message to
(e.g. "add a story for X")              the SAME session — agent already has
                                         Jira tools, acts immediately.        ───────►  More issues created
```

There is no human-confirmation step between analysis and Jira sync — the agent has full authority to determine the project key and sync the backlog autonomously, per its system prompt (`cma/prompts/system_prompt.md`).

## Prerequisites

- Python 3.10+
- An Anthropic API key with Managed Agents (beta) access
- A Slack app configured for Socket Mode (bot token + app-level token) — see "Slack App Setup" below
- (Optional) Jira Cloud API token — without it, the agent still analyzes and plans, it just can't sync to Jira

## Setup

```bash
cd "C:\GWC\Project Management Agent\Project management CMA"
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and fill in at minimum `ANTHROPIC_API_KEY`. Then provision the agent once:

```bash
python main_setup.py
```

This creates a Claude Managed Agent + Environment and writes `CMA_AGENT_ID` / `CMA_ENVIRONMENT_ID` back into `.env` automatically. Re-run it any time you edit the files under `cma/prompts/` — it updates the existing agent in place (publishing a new version) instead of creating a duplicate.

Now fill in the remaining `.env` values — `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `SLACK_CHANNEL_ID`, and the `JIRA_*` block if you want Jira sync — and start the daemon:

```bash
python main_live.py
```

## Slack App Setup

1. [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **Blank App**.
2. **OAuth & Permissions** → Bot Token Scopes: `channels:history`, `channels:read`, `files:read`, `chat:write`, `reactions:write`, `channels:manage`.
3. **Socket Mode** → enable it. **Basic Information** → App-Level Tokens → generate one with `connections:write` → this is `SLACK_APP_TOKEN`.
4. **Event Subscriptions** → enable → Subscribe to bot events → `message.channels`.
5. **Install to Workspace** → copy the **Bot User OAuth Token** (`xoxb-...`) → this is `SLACK_BOT_TOKEN`.
6. Invite the bot to your requirements channel: `/invite @YourAppName`. Copy the channel ID from *View channel details* → this is `SLACK_CHANNEL_ID`.

## Project layout

```
config.py                    Env loading & validation (setup vs. runtime)
logging_config.py            Centralized logging setup
utils.py                     JSON state persistence, filename/issue-key helpers
team_members.json            The virtual team roster (name, role, story-point cap)
team_roster.py                Loads + formats the roster for session kickoff messages
main_setup.py                 One-time: provision the Managed Agent + Environment
main_live.py                  Entry point: runs the Slack daemon
cma/
  agent_setup.py               Idempotent agent/environment creation & update
  session_manager.py            Session lifecycle: create, drain, tool dispatch, output download
  tools.py                      Custom Jira tool schemas + dispatcher
  prompts/
    system_prompt.md            Agent persona, autonomous workflow, guardrails
    requirements_analysis.md    Spec-writing methodology
    backlog_planning.md          Agile backlog methodology
integrations/
  jira_service.py               Thin wrapper around the `jira` SDK (token never leaves this process)
  attachment_extractor.py       PDF/text extraction from Slack file uploads
  slack_listener.py             Socket Mode event routing
state/                         Persisted thread→session mapping (survives daemon restarts)
outputs/                       Downloaded project_details.md files per project
tests/                         Import/config sanity tests (no API keys required)
```

## Security notes

- The Jira API token lives only in `.env` and inside `integrations/jira_service.py` (your own process) — it is never passed into the Managed Agent's sandbox. The agent only ever sees the five tool schemas in `cma/tools.py` and their JSON results.
- The agent has Jira tools from its first turn and acts autonomously (no human-confirmation gate) — if you want a manual approval step before Jira writes happen, the natural place to add it is a `permission_policy: {"type": "always_ask"}` on the Jira tool configs in `cma/agent_setup.py`, which pauses the session and waits for a `user.tool_confirmation` event per call.
- `.env.example` contains only obvious placeholder values — never commit a real `.env`.

## Known limitations / next steps

- This build has not been run end-to-end against live Anthropic/Slack/Jira credentials (none were available while building it) — static checks (imports, config validation, tool schema shape) were run instead. See `tests/test_config_and_imports.py`. Run `python main_setup.py` and a real Slack message through it as your first live test.
- The dedicated `#proj-<key>` Slack channel is created best-effort; if channel creation fails (e.g. name collision, missing scope) the sync still completes and reports the Jira links directly in the thread.
- Multi-project-in-flight is supported (state is keyed by Slack thread), but there's no cross-project dashboard yet — that would be the natural "Phase 2" from the original project's own roadmap.
"# project_management_agent" 
