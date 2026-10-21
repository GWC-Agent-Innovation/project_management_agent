# Feedback Widget

**Proposed Jira Project Key:** `FBW`

## Project Overview

The Feedback Widget is a lightweight, embeddable feedback collection tool for the GWC website. It gives visitors a simple, low-friction way to rate their experience (1-5 stars) and leave optional comments via a modal dialog, without navigating away from the page they're on. On the back end, an internal Admin Feedback List gives staff a single screen to review, filter, and triage all submitted feedback entries. The goal is to give the team a fast, low-cost pulse on visitor sentiment and surface actionable comments without adopting a heavyweight third-party survey platform.

## Core Requirements

### Functional Requirements

**User Feedback Form (Widget)**
- Visitors can open a modal dialog from the website (e.g. via a floating button/trigger) to submit feedback.
- The form captures a star rating (1-5, required) and a free-text comment (optional).
- Submitting the form validates that a rating has been selected before allowing submission.
- On successful submission, the visitor sees a confirmation/thank-you state and the modal closes or resets.
- Feedback submissions are persisted with a timestamp (and, where available, basic context such as the source page).

**Admin Feedback List**
- Authenticated admins can view a list of all submitted feedback entries (rating, comment, submitted date).
- Admins can filter the list — at minimum by star rating and by date range.
- The list supports pagination or scrolling to remain usable as entries grow.
- Admin access is restricted to authenticated staff only (not publicly accessible).

### Non-Functional Requirements

- The feedback modal must be lightweight and load quickly so it does not degrade the host page's performance.
- The widget should be responsive and usable on both desktop and mobile viewports.
- Admin endpoints/screens must require authentication; feedback submission endpoints must be protected against basic spam/abuse (e.g. rate limiting).
- The system should reliably persist submissions with no data loss on normal submission flow.

### Assumptions & Open Questions

- **Authentication for Admin**: The raw requirements do not specify an existing auth system to integrate with. Assumption: a simple authenticated admin login (email/password) will be built or an existing internal auth mechanism will be reused if one exists — please confirm.
- **Embedding mechanism**: Assumed the widget is embedded directly into the existing website's front end (same codebase) rather than as a separate cross-domain embeddable script. Please confirm if cross-site embedding (e.g. via `<script>` snippet on third-party domains) is required.
- **Filter fields for Admin List**: Assumed rating and date range are the primary filters; no additional fields (e.g. by page/source, by keyword search) were mentioned. Open to expanding scope if needed.
- **Volume/scale**: No expected traffic/volume was provided; non-functional requirements are written generically ("supports normal web traffic") pending more detail.
- **Notifications**: No requirement for email/Slack alerts on new feedback was mentioned; out of scope unless requested.

## Technology Stack

- **Frontend**: React (modal-based widget component + admin screen), standard for embedding interactive UI into an existing website.
- **Backend**: Node.js/Express REST API to receive and serve feedback submissions.
- **Database**: PostgreSQL for persisting feedback entries (rating, comment, timestamp, metadata).
- **Authentication**: Simple session/token-based auth for the Admin Feedback List.
- **Hosting/Infra**: Existing website hosting environment; standard CI/CD pipeline for deployment.

*(Stack choices reflect standard defaults for a small web app; no specialized stack — AI/ML, blockchain, etc. — was requested or implied.)*

## Action Plan / Tasks

### User Feedback Form (Modal Widget)
- [ ] Design modal UI (star rating input + comment textarea + submit/cancel actions)
- [ ] Build modal trigger + component in the website front end
- [ ] Implement client-side validation (rating required)
- [ ] Build `POST /feedback` API endpoint
- [ ] Create `feedback` database table/schema
- [ ] Add confirmation/thank-you state after successful submission

### Admin Feedback List
- [ ] Design admin list screen (table layout, filter controls)
- [ ] Build `GET /feedback` API endpoint with filter query params (rating, date range)
- [ ] Build admin list UI with filtering and pagination
- [ ] Add authentication guard to admin screen and API
- [ ] QA test: submission flow end-to-end, and admin filtering accuracy

## Immediate Next Steps

1. Confirm the admin authentication approach (new simple auth vs. reuse of existing system).
2. Finalize the database schema for feedback entries (fields, indexing for filters).
3. Build the `POST /feedback` API endpoint and the `feedback` table as the foundation both UI pieces depend on.
4. Build the Feedback Form modal UI and wire it to the API.
5. Build the Admin Feedback List screen with filtering, gated behind authentication.
