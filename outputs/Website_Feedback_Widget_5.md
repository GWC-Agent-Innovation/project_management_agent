# Website Feedback Widget

**Proposed Jira Project Key:** `FDBK`

## Project Overview

The Website Feedback Widget is a lightweight, embeddable feedback mechanism for the company website. It allows visitors to quickly rate their experience (1–5 stars) and leave optional comments through a simple modal dialog, without navigating away from the page they're on. Submitted feedback is captured and made available to internal staff through a dedicated admin screen where entries can be viewed and filtered. The goal is to give the business a fast, low-friction channel for collecting qualitative and quantitative visitor sentiment, and to give admins an easy way to review that feedback without needing direct database access.

## Core Requirements

### Functional Requirements

**User Feedback Form (Widget)**
- Display a modal/dialog that visitors can open from the website to submit feedback.
- Capture a star rating on a 1–5 scale (required).
- Capture a free-text comment field (optional).
- Validate input client-side before submission (e.g., rating must be selected).
- Submit the rating + comment to the backend and confirm successful submission to the user.
- Persist each submission (rating, comment, timestamp, and any available metadata such as source page) in a database.

**Admin Feedback List**
- Provide an admin-only screen listing all submitted feedback entries.
- Display rating, comment, and submission date/time for each entry.
- Allow admins to filter the list (e.g., by star rating and/or date range).
- Retrieve filtered results from the backend via a query-capable API endpoint.

### Non-Functional Requirements
- The widget must be lightweight and non-blocking — it should not noticeably impact page load performance.
- The modal should be responsive and usable on both desktop and mobile viewports.
- Feedback data must be stored reliably and be retrievable for reporting/filtering.
- Basic input validation and sanitation must be applied to prevent malformed or malicious submissions.
- The admin feedback list should be restricted to internal/admin users only.

### Assumptions & Open Questions
- **Admin authentication**: The raw requirement does not specify how admin access is secured. This spec assumes the admin screen sits behind whatever existing admin/auth mechanism the website already has; if none exists, a minimal access-gate should be scoped separately.
- **Embedding mechanism**: It is assumed the modal is triggered by an existing on-page button/link (e.g., a "Feedback" tab) rather than a new placement strategy; exact trigger UX is open for design input.
- **Filter fields**: The requirement says "filter submitted feedback entries" without specifying which fields. This spec assumes filtering by star rating and submission date range as the minimum viable filter set.
- **Volume/scale**: No expected traffic or submission volume was provided; standard web-scale assumptions apply (no special performance engineering required at this stage).

## Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| Frontend | JavaScript/HTML/CSS (component-based, e.g. React) | Standard choice for an embeddable interactive modal widget on a website |
| Backend | REST API (Node.js/Express or equivalent) | Simple CRUD/read endpoints for feedback submission and retrieval |
| Database | Relational database (e.g., PostgreSQL) | Structured storage of rating, comment, timestamp; supports filtering/querying |
| Admin UI | Same frontend framework as widget, separate protected route | Reuses component library; kept behind existing admin access |

*Note: No specific technologies were named in the source requirements, so the stack above reflects the standard, minimal choices for a small web widget + admin screen application.*

## Action Plan / Tasks

### User Feedback Form (Widget)
- [ ] Design modal UI mockup (star rating input + comment field + submit/cancel actions)
- [ ] Build the modal form component in the frontend
- [ ] Add client-side validation (rating required)
- [ ] Design feedback database table schema (rating, comment, timestamp, metadata)
- [ ] Implement `POST /api/feedback` endpoint with server-side validation and persistence
- [ ] Confirm successful submission to the user (success/error state in modal)

### Admin Feedback List
- [ ] Build admin feedback list UI with rating and date-range filters
- [ ] Implement `GET /api/feedback` endpoint supporting filter/query parameters
- [ ] Restrict admin screen access to internal/admin users

## Immediate Next Steps
1. Finalize the modal's visual design and trigger placement on the website (Alice, UI/UX).
2. Confirm the admin access/auth approach to apply to the admin feedback screen.
3. Define and create the feedback database schema (Frank, Database Engineer).
4. Build and wire up the `POST /api/feedback` submission flow end-to-end (form → API → DB).
5. Build the admin list view against the `GET /api/feedback` endpoint with filtering.
