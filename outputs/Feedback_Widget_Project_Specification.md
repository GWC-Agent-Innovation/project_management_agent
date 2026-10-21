# Feedback Widget — Project Specification

**Proposed Jira Project Key:** `FBW`

---

## 1. Project Overview

The Feedback Widget is a lightweight, embeddable feature for the GWC website that lets visitors quickly submit star-rating feedback and free-text comments, and gives internal admins a way to review and filter that feedback. The goal is to give the team a simple, low-friction channel for capturing visitor sentiment without building a full survey platform. Scope is intentionally minimal: a public-facing submission modal and an internal admin review screen. This is a small, self-contained feature rather than a full application, so the plan below is scoped as a single-sprint delivery.

---

## 2. Core Requirements

### Functional Requirements

**User Feedback Form (Modal)**
- Visitors can open a modal on the website to submit feedback.
- Modal supports a 1–5 star rating input (required).
- Modal supports a free-text comments field (optional, reasonable max length).
- Submission is validated client-side (rating required) before sending.
- Successful submission shows a confirmation state; failures show an inline error.
- Submitted feedback is persisted to a backend data store via an API endpoint.

**Admin Feedback List**
- An admin-only screen lists all submitted feedback entries (rating, comment, submitted date/time).
- Admin can filter the list (e.g., by star rating and/or date range).
- List is paginated or otherwise performant for a growing number of entries.
- Screen is restricted to authenticated admin users (basic access control).

### Non-Functional Requirements
- Widget must be lightweight and not noticeably impact host page load time.
- Modal should be responsive (usable on desktop and mobile viewports).
- Feedback submission endpoint should respond quickly (< 500ms typical) under normal load.
- Basic input sanitization/validation to prevent malformed or malicious submissions.
- Admin screen access should be gated behind authentication (even if minimal for v1).

### Assumptions & Open Questions
- **Authentication for Admin screen**: Raw requirement doesn't specify an auth mechanism. Assumption: a simple existing/basic admin login gate is sufficient for v1; full SSO/role management is out of scope unless clarified.
- **Embedding mechanism**: Not specified whether the widget is a JS snippet embedded on arbitrary pages or a component within an existing app shell. Assumption: it's built as a component/snippet that can be dropped into the existing website.
- **Data retention/export**: No mention of exporting or deleting feedback entries. Assumed out of scope for v1.
- **Volume expectations**: No specific concurrency/scale numbers given; assumed low-to-moderate traffic typical of a feedback widget (not high-scale).
- **Notifications**: No requirement for email/Slack alerts on new feedback; assumed out of scope for v1 unless requested later.

---

## 3. Technology Stack

- **Frontend**: React (component-based modal + admin list UI), standard CSS/component styling.
- **Backend**: Node.js/Express REST API (single endpoint group: submit feedback, list/filter feedback).
- **Database**: PostgreSQL (simple `feedback` table: id, rating, comment, created_at).
- **Auth (Admin)**: Basic auth-gated route for the admin screen (existing session/auth mechanism assumed, minimal implementation for v1).
- **Hosting/DevOps**: Existing website hosting/CI pipeline reused; no new infrastructure implied by requirements.

*Note: Stack choices reflect standard defaults for a small web widget + admin screen since no explicit stack was named in the requirements.*

---

## 4. Action Plan / Tasks

### User Feedback Form (Modal)
- [ ] Design modal UI (star rating control + comment textarea + submit/cancel states)
- [ ] Build modal component with client-side validation (rating required)
- [ ] Build `POST /api/feedback` endpoint to persist submissions
- [ ] Create `feedback` database table/schema
- [ ] Add success/error states and basic submission tests

### Admin Feedback List
- [ ] Design admin list screen (table layout + filter controls)
- [ ] Build `GET /api/feedback` endpoint with filter (rating, date range) + pagination support
- [ ] Build admin list UI consuming the endpoint, wired to filters
- [ ] Gate admin screen behind existing auth/login check
- [ ] QA pass: verify filtering, pagination, and access restriction

---

## 5. Immediate Next Steps

1. Confirm the admin authentication approach (reuse existing login vs. new minimal gate) before backend work starts.
2. Finalize the `feedback` table schema (fields, constraints) with the Database Engineer.
3. Build the star-rating modal UI and wire it to a new `POST /api/feedback` endpoint.
4. Build the admin list screen against a new `GET /api/feedback` endpoint with filtering.
5. QA the end-to-end flow (submit → persist → view/filter in admin) before calling the sprint complete.

---

## 6. Sprint Plan (Reference — see Slack summary for executive view)

**Scope classification:** Small (2 features) → 1 Epic, 4 Stories, 1 Sprint, minimal sub-tasks per Backlog Planning Methodology.

**Sprint 1 — Feedback Widget MVP (single sprint delivery)**
Goal: Deliver both the public feedback modal and the admin review screen end-to-end, including basic validation, persistence, filtering, and access control.

### Epic 1: Feedback Widget MVP
One Epic covering both the visitor-facing form and the admin review screen, since this is a single cohesive small-scope feature.

| # | Story | Points | Assignee | Sprint |
|---|-------|--------|----------|--------|
| 1 | Visitor Feedback Modal (rating + comments UI) | 5 | Bob Smith (Frontend) | Sprint 1 |
| 2 | Feedback Submission API + persistence | 5 | David Davis (Backend) | Sprint 1 |
| 3 | Admin Feedback List UI with filtering | 5 | Charlie Brown (Frontend) | Sprint 1 |
| 4 | Feedback List/Filter API + access control | 5 | Emily Evans (Backend) | Sprint 1 |

**Total: 4 Stories | 20 Story Points | 1 Epic | 1 Sprint**

#### Story 1: Visitor Feedback Modal
**As a** website visitor, **I want** to submit a star rating and comment through a modal, **so that** I can quickly share feedback without leaving the page.

- **Story Points**: 5
- **Assignee**: Bob Smith — Frontend Developer
- **Acceptance Criteria**:
  - Given the modal is open, when I select 1-5 stars and click submit, then my rating is required and the form will not submit without it.
  - Given I submit valid feedback, when the API call succeeds, then I see a confirmation message and the modal closes/resets.
  - Given the API call fails, when submission is attempted, then I see an inline error and can retry.
- **Sub-tasks**:
  - [ ] Build modal component with 1-5 star rating control and comment textarea
  - [ ] Wire client-side validation + submit/error/success states

#### Story 2: Feedback Submission API + Persistence
**As a** system, **I want** an endpoint that validates and stores submitted feedback, **so that** admins can later review it.

- **Story Points**: 5
- **Assignee**: David Davis — Backend Developer
- **Acceptance Criteria**:
  - Given a valid POST payload (rating 1-5, optional comment), when submitted, then a new feedback record is persisted with a timestamp.
  - Given an invalid payload (missing/out-of-range rating), when submitted, then the API returns a 400 with a clear error message.
- **Sub-tasks**:
  - [ ] Create `feedback` table schema (id, rating, comment, created_at) with Database Engineer
  - [ ] Implement `POST /api/feedback` endpoint with validation and error handling

#### Story 3: Admin Feedback List UI
**As an** admin, **I want** to view and filter submitted feedback in a list, **so that** I can understand visitor sentiment.

- **Story Points**: 5
- **Assignee**: Charlie Brown — Frontend Developer
- **Acceptance Criteria**:
  - Given feedback entries exist, when I open the admin screen, then I see a list showing rating, comment, and submitted date.
  - Given I apply a rating or date filter, when the filter is applied, then only matching entries are displayed.
- **Sub-tasks**:
  - [ ] Build admin list UI (table + filter controls) consuming the feedback API

#### Story 4: Feedback List/Filter API + Access Control
**As an** admin, **I want** a secure endpoint that returns filterable feedback data, **so that** only authorized users can view visitor feedback.

- **Story Points**: 5
- **Assignee**: Emily Evans — Backend Developer
- **Acceptance Criteria**:
  - Given a logged-in admin, when they call the list endpoint with filter params (rating, date range), then only matching, correctly paginated results are returned.
  - Given an unauthenticated request, when the endpoint is called, then it is rejected with a 401/403.
- **Sub-tasks**:
  - [ ] Implement `GET /api/feedback` endpoint with rating/date filtering and pagination
  - [ ] Add auth check/middleware to restrict access to admin users

**Capacity check**: Bob (5), Charlie (5), David (5), Emily (5) — all well under the 10 pt/sprint cap. QA (Grace/Henry), Alice (UI/UX), Frank (DB support), Ivy (DevOps), and Jack (Scrum Master) support across stories as needed but aren't primary owners for this small-scope sprint.
