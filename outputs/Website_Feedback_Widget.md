# Website Feedback Widget

**Proposed Jira Project Key:** `FBW`

## Project Overview

The Website Feedback Widget is a lightweight, embeddable feature that lets website visitors quickly rate their experience (1-5 stars) and leave optional comments through a modal dialog, without navigating away from the page they're on. Submitted feedback is stored centrally and made available to site administrators through a dedicated admin screen where entries can be viewed and filtered. The goal is to give the business a fast, low-friction way to collect qualitative and quantitative visitor sentiment and to give admins a simple tool to monitor that sentiment over time. This is a small, self-contained utility feature rather than a full application, so the plan below is intentionally scoped tight.

## Core Requirements

### Functional Requirements

**User Feedback Form (Widget)**
- Display a modal/dialog that visitors can open to submit feedback.
- Modal contains a 1-5 star rating control (required) and a free-text comments field (optional).
- Submitting the form sends the rating + comment (+ timestamp, and page URL/context if available) to the backend and shows a confirmation state.
- Basic client-side validation: a star rating must be selected before submission is allowed.

**Admin Feedback List**
- An authenticated admin screen listing all submitted feedback entries (rating, comment, submission date, source page if captured).
- Ability to filter the list (e.g., by star rating and/or date range).
- Paginated or scrollable list to handle growing volumes of feedback entries.

### Non-Functional Requirements
- The widget must be lightweight and must not noticeably impact page load performance.
- Admin screen access must be restricted to authenticated admin users only.
- The feedback submission API must validate input server-side (rating range, comment length) in addition to client-side checks.
- The UI should be responsive (usable on both desktop and mobile viewports).

### Assumptions & Open Questions
- No authentication system was specified for admins — it is assumed a basic admin login/auth mechanism already exists or will be stubbed minimally; if a full auth system is required, that would expand scope beyond this backlog.
- No specific technology stack, hosting, or existing codebase was mentioned — a standard modern web stack is assumed (see below).
- It's assumed feedback is anonymous (no requirement for tying feedback to a logged-in visitor account).
- Volume/scale expectations (e.g., number of submissions per day) were not specified; default assumption is low-to-moderate volume typical of a feedback widget.
- Export functionality (e.g., CSV export of feedback) was not requested and is out of scope unless clarified otherwise.

## Technology Stack

- **Frontend:** React (component-based modal widget + admin list view)
- **Backend:** Node.js with a REST API (e.g., Express) to handle feedback submission and retrieval
- **Database:** PostgreSQL (or equivalent relational DB) to store feedback entries
- **Testing:** Standard unit/integration testing for form validation and API endpoints

*(Only standard, obvious choices for a small web widget + admin screen are proposed; no specialized stacks are introduced since none were requested.)*

## Action Plan / Tasks

### User Feedback Form (Widget)
- [ ] Design the modal UI (star rating control + comment field + submit/cancel actions)
- [ ] Build the modal component and star-rating input in the frontend
- [ ] Implement client-side validation (rating required)
- [ ] Build `POST /feedback` API endpoint with server-side validation
- [ ] Create `feedback` table/schema in the database
- [ ] Wire up submission confirmation state in the UI

### Admin Feedback List
- [ ] Design the admin list screen layout (table + filter controls)
- [ ] Build `GET /feedback` API endpoint with filter query params (rating, date range)
- [ ] Build the admin list UI component with filtering and pagination
- [ ] Restrict admin screen access to authenticated admin users
- [ ] QA: validate filtering, pagination, and access restriction behavior

## Immediate Next Steps

1. Finalize the feedback data schema (fields: rating, comment, timestamp, source page, optional metadata).
2. Design the feedback modal UI (Alice) in parallel with backend API scaffolding (David/Emily).
3. Implement and unit-test the `POST /feedback` submission flow end-to-end first, since the admin list depends on data existing.
4. Build the admin list screen and filtering once submission flow is stable.
5. QA pass on both the widget and admin screen before release.
