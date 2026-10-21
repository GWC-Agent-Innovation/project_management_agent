# Website Feedback Widget

**Proposed Jira Project Key**: `FBW`

## Project Overview

The Website Feedback Widget is a lightweight, embeddable feature that lets website visitors quickly submit a star rating (1–5) and optional written comments through a modal popup. Submitted feedback is stored centrally and surfaced to internal staff via a simple admin screen where entries can be viewed and filtered. The goal is to give the business a low-friction way to capture visitor sentiment without building a full survey platform — fast to implement, easy to embed on existing pages, and simple for a non-technical admin to review.

## Core Requirements

### Functional Requirements

**User Feedback Form (Widget)**
- Display a modal/popup on the website that visitors can open to submit feedback.
- Capture a star rating from 1 to 5 (required).
- Capture an optional free-text comment field.
- Submit the feedback to the backend and confirm successful submission to the user (e.g. "Thanks for your feedback").
- Basic client-side validation (rating is required before submit; comment length capped).

**Admin Feedback List**
- Admin-facing screen listing all submitted feedback entries (rating, comment, submission date).
- Ability to filter the list (e.g. by star rating and/or date range).
- Paginated or scrollable list to handle growing volumes of feedback.
- Restricted to admin/internal users only (basic access control).

### Non-Functional Requirements
- The widget must be lightweight and not noticeably slow down host page load.
- Feedback submission should respond quickly (sub-second perceived response) with clear success/error state.
- Admin list should support at least a few thousand feedback records without performance degradation.
- Basic protection against spam/abuse on the public submission endpoint (e.g. simple rate limiting).
- Responsive design: the feedback modal must work on both desktop and mobile viewports.

### Assumptions & Open Questions
- No authentication system was specified for the admin screen — assumed a simple restricted/admin-only view is sufficient for this scope (exact auth mechanism, e.g. shared login vs. full user accounts, is an open question for the manager).
- No specific design/branding guidance was provided — assumed a clean, minimal modal consistent with typical website UI.
- Filtering criteria for the admin list were not explicitly specified — assumed filtering by rating and date range as the most common/useful filters; to be confirmed.
- No requirement was given for email notifications or analytics/export of feedback — out of scope unless clarified.
- Volume/scale expectations (expected number of submissions) were not provided — assumed low-to-moderate traffic typical of a feedback widget.

## Technology Stack

- **Frontend**: JavaScript/HTML/CSS-based embeddable widget (modal component), rendered with a standard frontend framework (e.g. React) for the widget and the admin screen.
- **Backend**: REST API (e.g. Node.js/Express or equivalent) to receive feedback submissions and serve the admin list/filter endpoints.
- **Database**: Relational database (e.g. PostgreSQL) to persist feedback entries (rating, comment, timestamp).
- **Infrastructure**: Standard web hosting/CI-CD pipeline for deploying the widget script and backend API.

*Note: Stack choices beyond "web app with frontend + backend + database" were not specified in the requirements; the above reflects standard defaults for this type of application.*

## Action Plan / Tasks

### User Feedback Form (Modal Widget)
- [ ] Design the feedback modal UI (star rating input + comment textarea + submit button)
- [ ] Build the modal component and trigger (open/close behavior)
- [ ] Implement client-side validation (required rating, comment length limit)
- [ ] Build `POST /feedback` API endpoint to accept and store submissions
- [ ] Add success/error confirmation state after submission

### Admin Feedback List
- [ ] Design the admin list screen layout (table/list + filter controls)
- [ ] Build `GET /feedback` API endpoint with filter query params (rating, date range)
- [ ] Build the admin list UI with filter controls and pagination
- [ ] Restrict admin screen access (basic admin-only guard)

### Cross-Cutting
- [ ] Define feedback database schema (rating, comment, created_at)
- [ ] Add basic rate limiting / spam protection to the submission endpoint
- [ ] QA test pass: form submission flows, filtering, responsive behavior

## Immediate Next Steps

1. Confirm admin access approach (existing login system vs. simple shared admin credential) with the manager.
2. Finalize the feedback database schema (fields, indexes for filtering by rating/date).
3. Build the modal widget UI and wire it to a stubbed submission endpoint to validate the end-to-end flow early.
4. Stand up the `POST /feedback` and `GET /feedback` endpoints against the real schema.
5. Build and QA the admin list/filter screen against live submitted data.
