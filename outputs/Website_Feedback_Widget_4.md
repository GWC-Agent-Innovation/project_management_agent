# Website Feedback Widget

**Proposed Jira Project Key:** `FDBK`

## Project Overview

The Website Feedback Widget is a lightweight feedback collection tool for the company website, aimed at capturing quick, structured input from visitors and giving internal admins a simple way to review it. The system consists of two user-facing surfaces: a public-facing modal where any website visitor can rate their experience (1–5 stars) and leave a comment, and an internal admin screen where staff can view and filter all submitted feedback entries. The goal is to give the team a fast, low-friction way to gauge visitor sentiment without adopting a heavyweight third-party survey tool, while keeping the implementation scoped tightly to the two requested screens.

## Core Requirements

### Functional Requirements

**Feedback Submission (Visitor-Facing)**
- Display a modal/dialog that visitors can trigger to open the feedback form.
- Capture a star rating from 1 to 5 (required).
- Capture free-text comments (optional, reasonable max length).
- Submit the rating + comment to the backend and persist it.
- Show a confirmation state after successful submission (and an error state on failure).

**Admin Feedback Management (Internal-Facing)**
- Provide an admin screen listing all submitted feedback entries (rating, comment, submission date/time).
- Support filtering the list (at minimum: by star rating; by date range if time allows).
- Paginate or scroll the list if entries grow large.

### Non-Functional Requirements
- The widget must be lightweight and must not noticeably impact website page-load performance.
- The admin screen should only be accessible to authorized/admin users (basic access restriction).
- Feedback data must be stored reliably (no silent data loss on submit).
- UI should be responsive (usable on both desktop and mobile for the visitor-facing modal).

### Assumptions & Open Questions
- No authentication system was specified for the admin screen — this spec assumes a basic admin-gated route/page exists or will be stubbed; full admin auth/RBAC is out of scope unless clarified.
- No design system, branding, or hosting/infrastructure constraints were mentioned — assumed to use the company's existing website stack conventions.
- "Filter submitted feedback entries" was not fully specified — assumed filtering by star rating is the primary requirement, with date-range filtering as a stretch/nice-to-have.
- No volume/scale expectations were given; assumed a small-to-moderate feedback volume typical of a lightweight widget (not high-throughput).
- No explicit deadline or budget constraint was mentioned in the source material.

## Technology Stack

- **Frontend:** JavaScript/TypeScript with a standard component framework (e.g. React) for the modal and admin list — the obvious standard for an embeddable website widget + admin screen.
- **Backend:** REST API (Node.js/Express or equivalent) to receive and serve feedback data.
- **Database:** Relational database (e.g. PostgreSQL) to persist feedback entries (rating, comment, timestamp).
- **Hosting/Infra:** Standard web hosting/CI pipeline consistent with the existing company website (no specialized infra requirements were stated).

*Note: No AI/ML, blockchain, or other specialized technology was requested or implied, so none is proposed.*

## Action Plan / Tasks

### User Feedback Form (Modal)
- [ ] Design the modal UI (trigger button/entry point, star rating input, comment textarea)
- [ ] Build the modal component with 1–5 star rating selector
- [ ] Add client-side form validation (rating required)
- [ ] Implement submit handler calling the feedback API
- [ ] Show success/error confirmation states
- [ ] Write QA test cases for submission flow (valid, missing rating, long comment)

### Admin Feedback List
- [ ] Design the admin list screen layout (table/list view)
- [ ] Build backend `POST /api/feedback` endpoint + DB schema (rating, comment, created_at)
- [ ] Build backend `GET /api/feedback` endpoint with filter query params (rating, date range)
- [ ] Build admin list UI consuming the `GET /api/feedback` endpoint
- [ ] Add filter controls (by rating, optionally by date) to the admin screen
- [ ] Restrict admin screen access to authorized users

## Immediate Next Steps

1. Design the feedback modal UI and star rating component (Alice, UI/UX).
2. Stand up the database schema and `POST /api/feedback` endpoint to accept submissions (Frank/David).
3. Build the modal component and wire it to the submission endpoint (Bob).
4. Build the admin list screen and `GET /api/feedback` endpoint with filtering (Charlie/Emily).
5. QA the end-to-end submission → admin review flow before release (Grace).
