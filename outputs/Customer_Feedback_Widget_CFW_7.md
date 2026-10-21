# Customer Feedback Widget (CFW)

**Proposed Jira Project Key:** `CFW`

## Project Overview

The Customer Feedback Widget (CFW) is a lightweight, embeddable feedback tool for the company website that lets visitors quickly rate their experience and leave comments, and gives internal staff a simple admin screen to review and filter what's been submitted. The goal is to give the business a low-friction channel for capturing voice-of-customer data without adding weight or complexity to the main site. The initial scope is intentionally narrow — a submission modal for visitors and a review/filter screen for admins — so it can be built, tested, and shipped quickly as a single, self-contained module.

## Core Requirements

### Functional Requirements

**Visitor Feedback Form**
- Display a modal/dialog on the website that visitors can open to submit feedback.
- Capture a star rating on a 1–5 scale (required).
- Capture free-text comments alongside the rating.
- Persist each submission (rating + comment + timestamp) to a backend store.
- Show the visitor a confirmation that their feedback was received.

**Admin Feedback List**
- Provide an admin-only screen listing all submitted feedback entries.
- Each entry should display the star rating, comment text, and submission date/time.
- Support filtering the list (e.g., by star rating and/or by date range) so admins can quickly find relevant feedback.
- Support pagination for the list so it stays usable as submissions grow.

### Non-Functional Requirements
- **Lightweight**: the widget must be embeddable without materially impacting page load time on the host site.
- **Usability**: the feedback modal should be simple enough to complete in a few seconds (low-friction UX).
- **Access control**: the admin feedback list must be restricted to authorized/admin users only.
- **Reliability**: feedback submissions should not be lost — API calls should validate input and confirm persistence before showing success to the user.

### Assumptions & Open Questions
- The transcript does not specify authentication/authorization mechanism for the admin screen — we assume a simple existing admin-auth layer will gate access; this should be confirmed with the client.
- No mention of anonymous vs. logged-in visitor identity — we assume feedback submissions are anonymous (no visitor account required).
- No specific volume/scale targets or SLAs were given — the widget is being designed as "lightweight," so no heavy infrastructure is assumed.
- No design mockups or branding guidelines were provided — the UI/UX Designer will need to confirm visual style with the client before/during Sprint 1.
- Filtering fields (rating, date range) are inferred from "view and filter submitted feedback entries" — exact filter fields should be confirmed with the client if more are desired (e.g., by page/source URL).

## Technology Stack

Since this is a website-embedded widget with an admin screen, the standard web application stack applies:

- **Frontend**: React (component-based modal widget + admin list UI)
- **Backend**: Node.js / Express REST API (`/api/feedback` endpoints)
- **Database**: PostgreSQL (structured storage for rating, comment, timestamp, and filter queries)
- **Testing**: Manual + automated QA test cases for submission and admin filtering flows
- **Deployment/CI**: Standard CI pipeline for build/test/deploy of the widget bundle and API

*(No AI/ML, blockchain, or other specialized technology was requested or is warranted by this scope.)*

## Action Plan / Tasks

### Feedback Modal (Visitor-Facing)
- [ ] Design modal UI (star rating input + comment textbox)
- [ ] Build modal component with client-side validation (rating required)
- [ ] Design feedback database schema (rating, comment, timestamp)
- [ ] Build `POST /api/feedback` endpoint with validation and persistence
- [ ] Show success/confirmation state after submission

### Admin Feedback List
- [ ] Design admin list UI (table with rating, comment, date columns)
- [ ] Build `GET /api/feedback` endpoint with pagination
- [ ] Build admin list UI with pagination controls
- [ ] Add filter controls (by star rating, by date range) to admin UI
- [ ] Extend `GET /api/feedback` endpoint to support filter query parameters

## Immediate Next Steps
1. Confirm admin authentication approach and branding/UX direction with the client.
2. Finalize the feedback database schema (rating, comment, timestamp, and any future fields).
3. Build the visitor feedback modal and its submission API first (core MVP).
4. Build the admin list screen with pagination, then layer in filtering.
5. Run QA pass on both submission and filtering flows before release.

---

## Sprint-Based Agile Plan

**Scope classification**: Small (2 core features: visitor feedback form, admin feedback list/filter) → **1 Sprint**, small backlog per proportional sizing rules.

### Sprint 1 — MVP: Feedback Capture & Admin Review (Weeks 1–2)
**Goal**: Ship the complete, working feedback loop — visitors can submit ratings/comments, and admins can view and filter them.

**Total Backlog**: 2 Epics | 3 User Stories | 6 Sub-tasks | **13 Story Points**

---

### Epic 1: Feedback Submission Widget
Deliver the visitor-facing modal for submitting a star rating and comment.

**Story 1 — Visitor Feedback Modal** (5 pts) — *Assignee: Bob Smith (Frontend Developer)* — Sprint 1
> As a website visitor, I want to submit a star rating and comment through a modal, so that I can quickly share feedback about my experience.

**Acceptance Criteria**
- Given a visitor opens the feedback widget, when they select a star rating (1-5) and optionally enter a comment and submit, then the feedback is saved and a confirmation message is shown.
- Given a visitor tries to submit without selecting a star rating, when they click submit, then a validation error is shown and the submission is blocked.
- Given the submission succeeds, when the API call completes, then the modal closes or resets within a few seconds.

**Sub-tasks**
- [ ] Build feedback modal UI component with 1–5 star rating input and comment field (incl. client-side validation) — *Bob Smith*
- [ ] Design DB schema and implement `POST /api/feedback` endpoint with validation and persistence — *David Davis*

---

### Epic 2: Admin Feedback Dashboard
Give admins a screen to review and filter submitted feedback.

**Story 2 — Admin Feedback List View** (5 pts) — *Assignee: Charlie Brown (Frontend Developer)* — Sprint 1
> As an admin, I want to view a paginated list of submitted feedback entries, so that I can monitor customer sentiment over time.

**Acceptance Criteria**
- Given feedback entries exist, when an admin opens the feedback list screen, then ratings, comments, and submission timestamps are displayed in a table.
- Given more entries exist than fit on one page, when the admin navigates pages, then the list paginates correctly without errors.

**Sub-tasks**
- [ ] Build admin feedback list UI with table layout and pagination controls — *Charlie Brown*
- [ ] Implement `GET /api/feedback` endpoint with pagination support — *Emily Evans*

**Story 3 — Filter Feedback Entries** (3 pts) — *Assignee: David Davis (Backend Developer)* — Sprint 1
> As an admin, I want to filter feedback entries by star rating and date range, so that I can quickly find relevant feedback.

**Acceptance Criteria**
- Given feedback entries with varying ratings, when the admin selects a rating filter, then only matching entries are displayed.
- Given feedback entries across multiple dates, when the admin selects a date range, then only entries within that range are displayed.

**Sub-tasks**
- [ ] Add filter controls (star rating, date range) to the admin list UI — *Charlie Brown*
- [ ] Extend `GET /api/feedback` endpoint to accept filter query parameters — *David Davis*

---

### Team Capacity Allocation — Sprint 1

| Team Member | Role | Story Points Owned | Within Cap (10)? |
|---|---|---|---|
| Bob Smith | Frontend Developer | 5 (Story 1) | ✅ |
| Charlie Brown | Frontend Developer | 5 (Story 2) | ✅ |
| David Davis | Backend Developer | 3 (Story 3) + supporting sub-tasks | ✅ |
| Emily Evans | Backend Developer | Sub-task support (Story 2 API) | ✅ |
| Alice Johnson | UI/UX Designer | Supports modal/admin UI design review | ✅ |
| Grace Wilson / Henry Taylor | QA Tester | QA pass on submission + filtering flows | ✅ |
| Ivy Thomas | DevOps Engineer | CI/CD & deployment support as needed | ✅ |
| Jack White | Scrum Master | Sprint facilitation | ✅ |

**Total Story Points**: 13 across 3 Stories / 2 Epics — well within team capacity for a single sprint.
