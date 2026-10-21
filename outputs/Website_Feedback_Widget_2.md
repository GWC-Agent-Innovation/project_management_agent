# Website Feedback Widget

**Proposed Jira Project Key:** `FDBK`

## Project Overview

The Website Feedback Widget is a lightweight, embeddable feedback system for the company website that lets visitors quickly rate their experience and leave comments without leaving the page. It consists of two halves: a customer-facing modal for submitting a 1-5 star rating plus a comment, and an internal admin screen where staff can review and filter all submitted feedback. The goal is to give the team a fast, low-friction way to start collecting qualitative and quantitative visitor feedback and to make that feedback easy to triage from a single admin view. Given the small, well-scoped nature of the request, this is planned as a single-sprint MVP delivery rather than a multi-phase rollout.

## Core Requirements

### Functional Requirements

**User Feedback Form (Widget)**
- Visitors can open a modal (e.g., via a floating button or trigger link) from any page on the website.
- The modal presents a 1-5 star rating control and a free-text comment field.
- Star rating is required before submission; comment is optional.
- On submit, the feedback is persisted (rating, comment, timestamp, and originating page) and the visitor sees a success confirmation.
- Invalid/incomplete submissions (e.g., no rating selected) show inline validation feedback and are not saved.

**Admin Feedback List**
- An authenticated admin screen lists all submitted feedback entries (rating, comment, submission date, source page).
- The list is paginated to remain usable as volume grows.
- Admins can filter the list — at minimum by star rating and by date range.
- An empty state is shown when no entries match the current filters.

### Non-Functional Requirements
- The widget must be lightweight and non-blocking — it should not noticeably impact page load time.
- The admin screen must be access-restricted (authenticated/admin-only access).
- The feedback submission endpoint should validate input server-side (rating must be an integer 1-5) regardless of client-side validation.
- The UI should be responsive and usable on both desktop and mobile viewports.

### Assumptions & Open Questions
- **Authentication**: The raw requirement does not specify how admins log in. We assume the admin screen will sit behind whatever existing site authentication/admin auth mechanism is available; if none exists yet, a minimal admin-only guard will be added as part of this scope.
- **Embedding mechanism**: It's assumed the modal is triggered by a simple button/link already present (or to be added) on the site; no requirement was given for a specific trigger placement, so this is left flexible/configurable.
- **Notifications**: No requirement was given for notifying staff of new feedback (e.g., email/Slack alerts) — out of scope unless requested.
- **Moderation/deletion**: No requirement was given for editing or deleting feedback entries from the admin screen — out of scope for this MVP unless requested later.
- **Volume/scale**: No specific traffic or storage expectations were given; standard pagination is assumed sufficient for MVP.

## Technology Stack

*No stack was explicitly specified in the requirements. The following reflects the standard, minimal choice for a small web widget + admin screen and should be confirmed with the team before implementation.*

- **Frontend**: JavaScript/HTML/CSS widget component (framework-agnostic modal), embeddable on existing site pages; admin screen as a standard web page/SPA view.
- **Backend**: REST API (e.g., Node.js/Express or equivalent already used by the site) exposing `POST /api/feedback` and `GET /api/admin/feedback`.
- **Database**: A relational store (e.g., PostgreSQL/MySQL) with a single `feedback` table (rating, comment, created_at, source_page).
- **Auth**: Reuse of existing site authentication for the admin-only route.

## Action Plan / Tasks

### User Feedback Form (Widget)
- [ ] Design modal UI (star rating control + comment field + submit/cancel) — UI/UX mockup
- [ ] Build the feedback modal component and wire up the trigger
- [ ] Add client-side validation (rating required)
- [ ] Design `feedback` database table (rating, comment, timestamp, source page)
- [ ] Implement `POST /api/feedback` endpoint with server-side validation and persistence
- [ ] Show success confirmation / inline error states in the modal

### Admin Feedback List
- [ ] Design admin list layout (table/cards, filter controls, pagination, empty state)
- [ ] Build admin feedback list UI with pagination
- [ ] Implement `GET /api/admin/feedback` endpoint (auth-protected, paginated)
- [ ] Add filter controls (star rating, date range) to the admin UI
- [ ] Extend the admin API to support rating/date-range filter query params
- [ ] QA: test coverage for submission validation and admin filtering

## Immediate Next Steps
1. Confirm the admin authentication mechanism to gate the new admin feedback screen.
2. Finalize the `feedback` database schema (Database Engineer) so both the submission and admin-read APIs can be built against it.
3. Build the feedback modal UI and the `POST /api/feedback` endpoint in parallel (Frontend + Backend).
4. Build the admin list UI and `GET /api/admin/feedback` endpoint, then layer in filtering.
5. QA pass on both the submission flow and the admin filtering before release.
