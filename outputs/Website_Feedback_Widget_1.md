# Website Feedback Widget

**Proposed Jira Project Key:** `FBW`

## Project Overview
GWC needs a lightweight feedback widget embedded on the company website so visitors can quickly rate their experience and leave comments, and so internal staff can review that feedback without needing access to a database or log files. The system has two user-facing surfaces: a public-facing **Feedback Modal** for visitors to submit a 1-5 star rating plus optional comments, and an **Admin Feedback List** where authorized staff can view and filter all submitted entries. The goal is a minimal, fast-to-ship widget — not a full survey platform — that gives the team a simple channel for capturing visitor sentiment.

## Core Requirements

### Functional Requirements
**User Feedback Form**
- Visitors can open a modal (triggered by a button/link on the site) containing a feedback form.
- Form captures a star rating from 1 to 5 (required) and a free-text comment field (optional, reasonable max length).
- Form validates that a rating is selected before allowing submission.
- On submit, feedback is persisted (rating, comment, timestamp) via an API call.
- User receives confirmation (success state) after submitting, and the modal closes/resets.

**Admin Feedback List**
- Admin-accessible screen lists all submitted feedback entries (rating, comment, submitted date).
- List supports filtering (e.g., by star rating and/or date range).
- List is readable at a glance — newest entries surfaced first by default.

### Non-Functional Requirements
- Widget must be lightweight — modal should load quickly and not block core site rendering.
- Feedback submission API should respond quickly enough for a smooth modal UX (sub-second typical response).
- Admin list view should be restricted to authorized/admin users only.
- Data persisted reliably — no feedback silently lost on submit.

### Assumptions & Open Questions
- **Admin authentication**: The raw requirement does not specify how admins log in or how access is restricted. Assumption: a simple existing/basic auth gate is reused rather than building a new auth system from scratch; this should be confirmed with the manager.
- **Filter fields**: Exact filter fields (rating only vs. rating + date range) were not specified in detail. Assumption: filter by star rating and date range, as the most common minimal set.
- **Embedding mechanism**: Not specified whether the modal is a standalone widget/script embed or built directly into the existing site codebase. Assumption: it is built as a component within the existing website codebase (not a third-party embeddable script), pending confirmation.
- **Volume/scale**: No expected traffic or feedback volume was given; NFRs above are kept minimal/reasonable rather than invented at a specific number.

## Technology Stack
- **Frontend**: JavaScript framework consistent with the existing website (e.g., React) for the modal component and admin list view.
- **Backend**: REST API (Node.js/Express or equivalent) to receive and serve feedback records.
- **Database**: Relational database (e.g., PostgreSQL) for a simple `feedback` table (id, rating, comment, created_at).
- **DevOps**: Standard CI pipeline to build/deploy the widget alongside the existing website.

*(No AI/ML, blockchain, or specialized infrastructure is implied by this requirement, so none is proposed.)*

## Action Plan / Tasks

**Feedback Modal (User-Facing)**
- [ ] Design modal UI (star rating control + comment textarea + submit button)
- [ ] Build modal component with open/close trigger
- [ ] Add client-side validation (rating required) and submit handler
- [ ] Design `feedback` DB schema/table
- [ ] Implement `POST /api/feedback` endpoint to persist rating + comment
- [ ] Show success/confirmation state after submit

**Admin Feedback List**
- [ ] Build admin list UI (table of entries: rating, comment, date)
- [ ] Implement `GET /api/feedback` endpoint with rating/date filter query params
- [ ] Add filter controls to admin UI (rating, date range)
- [ ] QA: test plan covering submission, validation, and filtering

## Immediate Next Steps
1. Confirm the admin authentication approach and exact filter fields with the manager (open questions above).
2. Design and migrate the `feedback` database table.
3. Build the `POST /api/feedback` endpoint and wire it to the feedback modal.
4. Build the feedback modal UI and connect it to the live endpoint.
5. Build the admin list screen and `GET /api/feedback` filtering endpoint in parallel.
