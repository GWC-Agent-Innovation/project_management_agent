# Customer Feedback Widget (CFW)
**Jira Project Key:** `CFW`

## Project Overview
The Customer Feedback Widget (CFW) is a lightweight, embeddable feedback tool for the client's website that lets visitors quickly rate their experience (1-5 stars) and leave a comment through a simple modal, without leaving the page they're on. Internally, the client's team needs a companion admin screen to review, browse, and filter all submitted feedback so they can monitor sentiment and act on comments. The goal is a minimal, fast-to-ship widget that closes the loop between visitor sentiment and internal visibility, with no heavyweight survey infrastructure required.

## Core Requirements

### Functional Requirements
- **Visitor Feedback Form**
  - Present a modal/dialog on the website that visitors can open to submit feedback.
  - Capture a star rating on a 1-5 scale (required).
  - Capture a free-text comment field alongside the rating.
  - Submit the entry to the backend and show the visitor a confirmation/success state.
- **Admin Feedback List**
  - Provide an internal/admin-only screen listing all submitted feedback entries (rating, comment, submitted date).
  - Support filtering the list (e.g., by rating value, and/or date range).
  - Read-only view for this initial scope (no edit/delete requirements were specified).

### Non-Functional Requirements
- Widget must be lightweight and non-blocking to the host page's load performance (embeddable modal, not a full page redirect).
- Admin feedback list should be restricted to authorized/admin users only.
- Widget UI should be responsive and usable on both desktop and mobile viewports.
- Feedback submissions should be validated server-side (e.g., rating required and within 1-5 range) before persisting.

### Assumptions & Open Questions
- **Authentication for Admin screen**: The requirements do not specify how admins log in. Assumption: the admin list sits behind whatever existing authentication the client's website/admin panel already uses; a full auth system is out of scope for this widget unless clarified otherwise.
- **Embedding mechanism**: Not specified whether the widget is a JS snippet embedded on third-party pages or a component within the client's own existing site codebase. Assumption: it is built as a component within the client's existing web app for this initial scope.
- **Filter fields for Admin List**: Only "filter submitted feedback" was mentioned without specifying exact filter fields. Assumption: filter by star rating and by submission date range as the minimum useful set.
- **Comment field required or optional**: Not specified. Assumption: star rating is required, comment is optional.
- **Notifications**: No mention of email/Slack alerts on new feedback — assumed out of scope for this release.

## Technology Stack
- **Frontend**: React (component-based modal + admin list UI, standard for embeddable web widgets)
- **Backend**: Node.js/Express REST API (lightweight endpoints for submit/list feedback)
- **Database**: PostgreSQL (simple relational storage for feedback entries: rating, comment, timestamp)
- **Hosting/Infra**: Standard web hosting with CI/CD pipeline for the widget bundle and admin app

*(No AI/ML, blockchain, or specialized stacks are warranted by these requirements.)*

## Action Plan / Tasks

### Feedback Modal (Visitor-facing)
- [ ] Build the feedback modal component (open/close behavior, trigger button)
- [ ] Implement 1-5 star rating input control
- [ ] Add comment text area field
- [ ] Wire up client-side validation (rating required)
- [ ] Apply visual styling consistent with client branding
- [ ] Build `POST /api/feedback` endpoint with server-side validation
- [ ] Design and create the `feedback` database table/schema
- [ ] Show success/confirmation state after submission

### Admin Feedback List Page
- [ ] Build admin list UI (table/list of feedback entries)
- [ ] Add filter controls (by rating, by date range)
- [ ] Build `GET /api/feedback` endpoint supporting filter query params
- [ ] Restrict access to the admin screen to authorized users

## Immediate Next Steps
1. Confirm the two open questions (admin auth approach, and exact filter fields) with the client before finalizing the schema and API contract.
2. Stand up the `feedback` database table and the `POST /api/feedback` endpoint first, since the admin list depends on data existing to display.
3. Build the visitor-facing modal UI in parallel and connect it to the submission endpoint.
4. Build the admin list UI and filtering once the list/read endpoint is available.
5. Run a short QA pass across both flows (submission + admin filtering) before release.
