# Customer Feedback Widget (CFW)
**Jira Project Key:** `CFW`

## 1. Project Overview
The Customer Feedback Widget (CFW) is a lightweight, embeddable widget for the company website that lets visitors quickly rate their experience and leave comments without navigating away from the page. It consists of two halves: a public-facing feedback modal for visitors, and an internal admin screen where staff can review and filter the feedback that comes in. The goal is a simple, low-friction way to capture qualitative and quantitative customer sentiment (star rating + free-text comment) and give the team a single place to monitor it, without the overhead of a full third-party feedback platform.

## 2. Core Requirements

### Functional Requirements
**Visitor Feedback Form**
- A modal dialog, triggered from the website, that visitors can open to submit feedback.
- A 1–5 star rating selector (required).
- A free-text comment field (optional).
- Client-side validation preventing submission without a rating.
- A confirmation state/message after successful submission.
- Persistence of each submission (rating, comment, timestamp) to a backend store.

**Admin Feedback List**
- An admin-only screen listing submitted feedback entries (rating, comment, submitted date).
- Pagination (or equivalent) for browsing entries as volume grows.
- An empty state when no feedback has been submitted yet.
- Filtering of the list by star rating and by date range.

### Non-Functional Requirements
- Widget must be lightweight and embeddable without materially impacting page load time.
- Admin screen should be accessible only to authorized/admin users (basic access restriction assumed; see open questions).
- Feedback submission API should validate input server-side (reject ratings outside 1–5) regardless of client-side checks.
- Responsive UI for both the visitor modal and the admin list (desktop + mobile widths).

### Assumptions & Open Questions
- **Authentication for the admin screen** was not specified — we are assuming a basic admin-gated view exists or will be provided by an existing auth system. Please confirm whether CFW needs to build its own admin login or plug into an existing one.
- **Where the widget is triggered from** (a floating button, a link, an existing page element) was not specified — assumed to be a simple trigger button/link that opens the modal.
- **Volume expectations** (e.g., number of expected submissions) were not specified; pagination is included as a reasonable default rather than a stated requirement.
- No specific browser support, localization, or branding requirements were mentioned — none are assumed beyond standard modern browser support.

## 3. Technology Stack
| Layer | Technology | Rationale |
|---|---|---|
| Frontend | React (modal + admin list components) | Standard choice for an interactive widget + admin SPA screen |
| Backend | Node.js / Express REST API | Lightweight API to handle feedback submission and retrieval |
| Database | PostgreSQL | Relational storage for structured feedback records (rating, comment, timestamp) |
| Testing | Jest / integration test suite | Validate API input rules and UI behavior |
| Deployment | Existing web infra (CI/CD via DevOps) | No new infra requirements were stated |

*Note: no technology was explicitly specified in the requirements; the above reflects the standard stack for a small web widget + admin screen.*

## 4. Action Plan / Tasks

### Visitor Feedback Modal
- [ ] Design modal UI (star rating input + comment textarea)
- [ ] Build modal component and trigger integration
- [ ] Add client-side validation (rating required)
- [ ] Build `POST /api/feedback` endpoint with server-side validation
- [ ] Design and create `feedback` database table (rating, comment, submitted_at)
- [ ] Show confirmation state after successful submission

### Admin Feedback List Page
- [ ] Build admin feedback list UI with pagination
- [ ] Build `GET /api/feedback` endpoint
- [ ] Add empty-state UI for zero feedback entries
- [ ] Add filter controls (rating, date range)
- [ ] Implement filter query params on the feedback list endpoint

## 5. Immediate Next Steps
1. Confirm admin access/authentication approach (new vs. existing system).
2. Finalize the `feedback` table schema (fields, types, constraints) with the Database Engineer.
3. Build the feedback modal UI and wire it to a stubbed submission endpoint.
4. Stand up the `POST /api/feedback` and `GET /api/feedback` endpoints with validation.
5. Build the admin list screen and layer in filtering once the base list is working.

---

# Sprint-Based Agile Plan

## Sprint Summary
- **Scope size:** Small (2 core features) → 1 Sprint, 2 Epics, 4 Stories.
- **Sprint 1 Goal (MVP):** Ship a working end-to-end feedback loop — visitors can submit rated feedback, and admins can view and filter it.
- **Total Backlog:** 16 Story Points across 2 Epics / 4 Stories / 6 Sub-tasks.
- **Estimated Timeline:** 1 Sprint (~1–2 weeks).

## Epic & Story Breakdown

### Epic 1: Visitor Feedback Capture
Enable website visitors to submit a star rating and comment via a modal, and persist it reliably.

**Story 1 — Feedback Submission Modal** *(5 pts, Sprint 1, Assignee: Bob Smith – Frontend Developer)*
> As a website visitor, I want to open a feedback modal and submit a 1–5 star rating with an optional comment, so that I can quickly share my experience without leaving the page.

Acceptance Criteria:
- Given a visitor clicks the feedback trigger, when the modal opens, then it shows a 5-star selector and a comment textarea.
- Given a visitor selects a rating and clicks Submit, when the submission succeeds, then a confirmation message is displayed and the modal closes.
- Given a visitor clicks Submit without selecting a rating, when validated, then an inline error is shown and nothing is submitted.

Sub-tasks:
- [ ] Build feedback modal UI (star rating + comment textarea) — Bob Smith
- [ ] Implement `POST /api/feedback` endpoint with input validation — David Davis

**Story 2 — Feedback Persistence** *(3 pts, Sprint 1, Assignee: Frank Miller – Database Engineer)*
> As the system, I need submitted feedback (rating, comment, timestamp) persisted in a database, so that it is available for admin review.

Acceptance Criteria:
- Given a valid submission, when the API receives it, then a new row is created in the `feedback` table with rating, comment, and `submitted_at`.
- Given a rating outside 1–5, when submitted, then the API rejects it with a 400 error and no row is created.

Sub-tasks:
- [ ] Design and create the `feedback` database schema/table — Frank Miller

*(Reasoning: this story is schema-focused and owned by the Database Engineer; only 1 sub-task is needed since it complements Story 1's API sub-task.)*

### Epic 2: Admin Feedback Management
Give admins a screen to review and filter incoming feedback.

**Story 3 — Admin Feedback List** *(5 pts, Sprint 1, Assignee: Charlie Brown – Frontend Developer)*
> As an admin, I want to view a list of all submitted feedback entries, so that I can monitor customer sentiment over time.

Acceptance Criteria:
- Given feedback entries exist, when the admin opens the feedback screen, then a paginated list shows rating, comment, and date per entry.
- Given no feedback entries exist, when the admin opens the screen, then an empty-state message is shown instead of a blank list.

Sub-tasks:
- [ ] Build admin feedback list UI with pagination — Charlie Brown
- [ ] Implement `GET /api/feedback` endpoint — Emily Evans

**Story 4 — Filter Feedback Entries** *(3 pts, Sprint 1, Assignee: Emily Evans – Backend Developer)*
> As an admin, I want to filter feedback entries by star rating and date range, so that I can quickly find relevant feedback.

Acceptance Criteria:
- Given the admin feedback list, when the admin selects a rating filter, then only matching entries are displayed.
- Given the admin feedback list, when the admin selects a date range, then only entries within that range are displayed.

Sub-tasks:
- [ ] Implement filter UI controls and filter query params on `GET /api/feedback` — Emily Evans

## Team Capacity Allocation (Sprint 1)
| Team Member | Role | Points Owned | Cap |
|---|---|---|---|
| Bob Smith | Frontend Developer | 5 | 10 |
| Charlie Brown | Frontend Developer | 5 | 10 |
| Frank Miller | Database Engineer | 3 | 10 |
| Emily Evans | Backend Developer | 3 | 10 |
| David Davis | Backend Developer | (supporting sub-task) | 10 |

*All owners are well under the 10-point-per-sprint cap; no rebalancing needed for this small scope.*
