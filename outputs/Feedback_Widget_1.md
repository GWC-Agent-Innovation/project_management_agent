# Feedback Widget

**Proposed Jira Project Key:** `FDBK`

## Project Overview

The Feedback Widget is a lightweight, embeddable feedback mechanism for the GWC website that lets visitors quickly rate their experience (1-5 stars) and leave optional comments through a modal dialog. Submitted feedback is captured and made available to internal staff through a simple admin screen where entries can be viewed and filtered. The goal is to give the team a fast, low-friction way to collect qualitative and quantitative visitor sentiment without adding a heavyweight third-party analytics tool. This is a small, focused two-feature project intended to ship in a single sprint.

## Core Requirements

### Functional Requirements

**User Feedback Form (Visitor-facing)**
- Display a modal/dialog that visitors can open from anywhere on the website to submit feedback.
- Allow selection of a star rating from 1 to 5 (required field).
- Allow an optional free-text comment field alongside the rating.
- Submit the rating + comment to the backend and confirm successful submission to the user (e.g. a success message/toast).
- Basic client-side validation (rating must be selected before submit).

**Admin Feedback List (Admin-facing)**
- An authenticated admin screen listing all submitted feedback entries (rating, comment, submission date/time).
- Ability to filter the list, at minimum by star rating and/or date range.
- Paginated or scrollable list view to handle a growing number of entries.

### Non-Functional Requirements
- The modal should be lightweight and not noticeably impact page load performance.
- Feedback submissions should persist reliably (no data loss on submit).
- Admin screen should only be accessible to authorized/admin users.
- The widget should be responsive and usable on both desktop and mobile viewports.

### Assumptions & Open Questions
- **Assumption:** Admin authentication/authorization already exists or a minimal auth gate is acceptable for this MVP — the source material did not specify an existing admin login system, so a basic protected route is assumed rather than a full auth system build-out.
- **Open question:** Should the widget be embeddable on multiple external sites, or is it scoped to GWC's own website only? Assumed: GWC's own website only.
- **Open question:** No specific filter fields beyond rating/date were mentioned — assumed these two are sufficient for MVP; additional filters (e.g. keyword search on comments) can be added later if needed.
- **Open question:** No volume/scale requirements were given; assumed a standard low-to-moderate traffic feedback tool (not high-throughput).

## Technology Stack

- **Frontend:** React (component-based modal + admin list UI, responsive by default)
- **Backend:** Node.js / Express REST API (standard choice for a lightweight widget backend)
- **Database:** PostgreSQL (structured storage for rating, comment, timestamp, filterable fields)
- **DevOps:** Basic CI pipeline for build/test/deploy of the widget and admin screen

*(Only standard web-app stack components are proposed — no specialized AI/ML, blockchain, or other tooling, as none was indicated by the requirements.)*

## Action Plan / Tasks

### User Feedback Form
- [ ] Design modal UI (star rating control + comment textarea) — Figma/wireframe
- [ ] Build modal component in React with open/close trigger
- [ ] Implement client-side validation (rating required)
- [ ] Build `POST /feedback` API endpoint
- [ ] Create `feedback` database table/schema
- [ ] Show success/error confirmation state in the modal

### Admin Feedback List
- [ ] Design admin list screen layout (table + filter controls)
- [ ] Build admin list React screen with pagination
- [ ] Implement filter controls (by rating, by date range)
- [ ] Build `GET /feedback` API endpoint with filter query params
- [ ] Protect admin screen/route behind auth check
- [ ] QA pass: verify submission flow end-to-end and filter accuracy

## Immediate Next Steps

1. Finalize the modal and admin screen UI design (Alice) so frontend build can start immediately.
2. Stand up the `feedback` database schema (Frank) so both frontend and backend can build against it in parallel.
3. Build the `POST /feedback` submission endpoint and wire it to the modal (David + Bob).
4. Build the `GET /feedback` filtered listing endpoint and wire it to the admin screen (Emily + Charlie).
5. Run QA pass on the full submit → store → view/filter flow before calling the sprint complete (Grace/Henry).

---

## Sprint Plan Summary

- **Total Scope:** 2 Epics, 4 User Stories, 6 Sub-tasks, 16 Story Points
- **Sprints:** 1 Sprint (small, focused scope — fits within team capacity in a single sprint)
- **Sprint 1 Goal (MVP / Full Delivery):** Ship both the visitor feedback modal and the admin feedback list, fully wired end-to-end, including basic filtering and QA sign-off.

## Backlog Breakdown

### Epic 1: User Feedback Form
Visitor-facing modal to capture a star rating and optional comment, persisted via API.

**Story 1 — As a visitor, I want to submit a star rating and comment through a modal, so that I can quickly share feedback about my experience.**
- **Story Points:** 5
- **Assignee:** Bob Smith (Frontend Developer)
- **Sprint:** Sprint 1
- **Acceptance Criteria:**
  - Given the feedback modal is open, when I select a star rating and click submit without a comment, then my feedback is submitted successfully.
  - Given the modal is open, when I try to submit without selecting a rating, then I see a validation message and the submission is blocked.
  - Given a successful submission, when the API responds, then I see a confirmation message and the modal closes.
- **Sub-tasks:**
  - [ ] Build the feedback modal component (star selector + comment textarea) — Bob Smith
  - [ ] Wire modal submit action to the `POST /feedback` API with client-side validation — Bob Smith

**Story 2 — As the system, I need a backend endpoint and schema to store submitted feedback, so that no submissions are lost.**
- **Story Points:** 3
- **Assignee:** David Davis (Backend Developer)
- **Sprint:** Sprint 1
- **Acceptance Criteria:**
  - Given a valid rating (1-5) and optional comment, when `POST /feedback` is called, then a new feedback record is persisted with a timestamp.
  - Given an invalid or missing rating, when `POST /feedback` is called, then the API returns a 400 validation error.
- **Sub-tasks:**
  - [ ] Create `feedback` table schema (rating, comment, created_at) — Frank Miller
  - [ ] Implement `POST /feedback` endpoint with validation — David Davis

### Epic 2: Admin Feedback List
Admin-facing screen to review and filter submitted feedback entries.

**Story 3 — As an admin, I want to view a list of submitted feedback entries with filtering, so that I can review visitor sentiment efficiently.**
- **Story Points:** 5
- **Assignee:** Charlie Brown (Frontend Developer)
- **Sprint:** Sprint 1
- **Acceptance Criteria:**
  - Given feedback entries exist, when I open the admin list screen, then I see rating, comment, and submission date for each entry.
  - Given I apply a rating or date-range filter, when the filter is submitted, then only matching entries are displayed.
  - Given the list has many entries, when I scroll/paginate, then additional entries load without errors.
- **Sub-tasks:**
  - [ ] Build admin list screen with table + pagination — Charlie Brown
  - [ ] Build filter controls (rating, date range) and connect to API query params — Charlie Brown

**Story 4 — As an admin, I need a backend endpoint to fetch and filter feedback entries, so that the admin screen can display accurate, scoped results.**
- **Story Points:** 3
- **Assignee:** Emily Evans (Backend Developer)
- **Sprint:** Sprint 1
- **Acceptance Criteria:**
  - Given no filters are applied, when `GET /feedback` is called, then all entries are returned (paginated).
  - Given rating and/or date-range filters are passed as query params, when `GET /feedback` is called, then only matching entries are returned.
- **Sub-tasks:**
  - [ ] Implement `GET /feedback` endpoint with rating/date filter query params — Emily Evans
  - [ ] QA end-to-end test: submit feedback → verify it appears/filters correctly in admin list — Grace Wilson

## Team Capacity Allocation (Sprint 1)

| Team Member | Role | Points Assigned | Capacity |
|---|---|---|---|
| Bob Smith | Frontend Developer | 5 | 10 |
| Charlie Brown | Frontend Developer | 5 | 10 |
| David Davis | Backend Developer | 3 | 10 |
| Emily Evans | Backend Developer | 3 | 10 |
| Frank Miller | Database Engineer | (sub-task, part of Story 2) | 10 |
| Grace Wilson | QA Tester | (sub-task, part of Story 4) | 10 |

**Total Story Points: 16** across 2 Epics / 4 Stories / 6 Sub-tasks — all within Sprint 1, well under the 10-point-per-person capacity limit for every assignee.
