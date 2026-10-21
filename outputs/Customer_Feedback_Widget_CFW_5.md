# Customer Feedback Widget (CFW)

**Proposed Jira Project Key:** `CFW`

## Project Overview

The Customer Feedback Widget (CFW) is a lightweight, embeddable feedback mechanism for the company website that lets visitors quickly rate their experience and leave optional comments. The widget is intended to be simple and unobtrusive, appearing as a modal that visitors can trigger from any page. Internally, the business needs a way to review and make sense of this incoming feedback, so the project also includes a minimal admin screen for staff to view and filter submitted entries. The ultimate goal is to give the business a fast, low-friction channel for capturing customer sentiment and a simple internal tool for acting on it — without the overhead of a full-blown survey platform.

## Core Requirements

### Functional Requirements

**Visitor Feedback Submission**
- Provide a modal (dialog) accessible from the website that visitors can open to submit feedback.
- Modal must include a 1–5 star rating control (required).
- Modal must include a free-text comment field (optional).
- Client-side validation: a star rating must be selected before the form can be submitted; comment is not required.
- On successful submission, the visitor sees a confirmation state; on failure, a clear error state is shown.
- Submitted feedback (rating, comment, timestamp, and originating page/URL) is persisted to a backend data store.

**Admin Feedback Management**
- Provide an internal/admin screen listing all submitted feedback entries (rating, comment, submission date/time, source page).
- Support filtering the list by star rating and by date range.
- Provide a clear empty state when no feedback (or no matching filtered feedback) exists.

### Non-Functional Requirements
- The widget must be lightweight and must not noticeably degrade page load performance on the host site.
- The admin screen should only be accessible to authorized/internal users (basic access control assumed; see Open Questions).
- The feedback submission API should validate input server-side (rating range, required fields) regardless of client-side checks.
- The solution should be simple to embed/integrate into the existing website (e.g., a script include or component mount point).

### Assumptions & Open Questions
- **Authentication for the admin screen** was not specified — we are assuming a basic authenticated/internal-only admin view is required, but the specific auth mechanism (existing SSO vs. new simple login) needs client confirmation.
- **Where the widget is triggered from** (a floating button, a link in the footer, etc.) was not specified — assumed to be a simple trigger button/link that opens the modal, exact placement to be confirmed with the client.
- **Volume/scale expectations** (expected number of submissions) were not provided; assumed low-to-moderate volume suitable for a simple relational data store, not a high-throughput system.
- **Export or notification features** (e.g., emailing new feedback, exporting to CSV) were not mentioned and are out of scope unless the client confirms they're needed.
- No mention of multi-site/multi-tenant support — assumed single site/single deployment for now.

## Technology Stack

- **Frontend:** JavaScript/React-based widget component for the feedback modal, embeddable into the existing website; a simple React-based admin page for the feedback list.
- **Backend:** REST API (Node.js/Express or equivalent) exposing endpoints to submit and retrieve feedback.
- **Database:** Relational database (e.g., PostgreSQL) to persist feedback entries (rating, comment, timestamp, source URL).
- **Hosting/Infra:** Standard web hosting for the API and static assets; no specialized infrastructure required given current scope.

*(Only a standard web app stack is proposed here — no specialized frontend framework, database engine, or infrastructure was named in the requirements, and none of the requirements call for AI/ML, blockchain, or similar specialized technology.)*

## Action Plan / Tasks

### Feedback Modal (Visitor-Facing)
- [ ] Design the feedback modal UI (star rating control + comment field + trigger button)
- [ ] Build the modal component with client-side validation and success/error states
- [ ] Wire the modal submission to the backend API

### Feedback Submission API & Storage
- [ ] Design the feedback data model (rating, comment, timestamp, source URL)
- [ ] Implement `POST /api/feedback` with server-side validation (rating 1–5 required)
- [ ] Persist submissions to the database

### Admin Feedback List Page
- [ ] Implement `GET /api/feedback` list endpoint
- [ ] Build the admin feedback list UI (table/list view with empty state)
- [ ] Restrict access to the admin page to authorized users

### Feedback Filtering
- [ ] Add rating and date-range filter parameters to `GET /api/feedback`
- [ ] Build filter controls (star-rating dropdown, date range picker) in the admin UI

## Immediate Next Steps

1. Confirm the admin authentication approach with the client (existing SSO vs. new basic login).
2. Confirm where/how the feedback modal should be triggered on the live site.
3. Finalize the feedback data model (fields, source URL capture) with the Database Engineer.
4. Begin implementation of the feedback modal UI and the `POST /api/feedback` endpoint in parallel, since they are the highest-priority MVP path.
5. Build the admin list view once submission storage is in place, then layer in filtering.
