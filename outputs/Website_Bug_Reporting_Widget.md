# Website Bug Reporting Widget

**Proposed Jira Project Key:** `BUGRP`

---

## Project Overview

GWC wants to give website visitors a simple, self-service way to report problems they encounter while browsing the site. The feature consists of an always-visible "Report a Problem" button/widget that opens a modal form. Visitors select a bug category, describe the issue, and may optionally attach a screenshot and leave an email address for follow-up. On submission, the report is sent to the team and the visitor sees a confirmation message. The goal is to lower the friction for visitors reporting bugs, giving the team a structured, centralized stream of user-reported issues instead of relying on ad-hoc emails or missed feedback.

---

## Core Requirements

### Functional Requirements

**Widget & Entry Point**
- A "Report a Problem" button/widget must be visible on the website (persistent, accessible from any page).
- Clicking the button/widget opens a modal dialog containing the report form.

**Bug Report Form**
- User can select a bug category from a fixed list: `UI/Design`, `Functionality`, `Performance`, `Other`.
- User can enter a free-text description of the problem (required field).
- User can optionally upload a screenshot image.
- User can optionally enter an email address for follow-up.
- User submits the form via a "Submit Report" button.

**Submission Handling**
- On submit, the report data (category, description, optional screenshot, optional email) is sent to the backend and persisted.
- After a successful submission, the user is shown a clear success message/confirmation in the modal.

### Non-Functional Requirements

- The modal and widget must be responsive and usable on both desktop and mobile viewports.
- Screenshot uploads should be restricted to common image types (e.g. PNG, JPG) with a reasonable max file size to avoid abuse.
- Description field is required; category, screenshot, and email are optional except category and description are mandatory per the flow (category is a required selection to route the report, description is required to have any content to act on).
- Form must validate required fields client-side and give inline error feedback before allowing submission.
- Submitted data must be stored reliably (no silent data loss) and screenshots stored as retrievable file references.
- Basic protection against spam/abuse on the public-facing submission endpoint (e.g. rate limiting) is recommended.

### Assumptions & Open Questions

- **Category as required field**: the requirement lists category as a selectable option but does not explicitly say "required" — we assume it is required since it drives issue routing/triage. Please confirm.
- **Screenshot storage**: no file size/type limits were specified; we've assumed sensible defaults (PNG/JPG, small size cap) pending confirmation.
- **Notifications**: the requirement doesn't specify whether the team should be notified (e.g. email/Slack alert) when a new report comes in, or whether reports are only viewed via an admin/reporting view. Assumed out of scope for this phase — reports are stored and viewable via direct DB/API access only, unless clarified.
- **Admin view**: no requirement was given for an internal dashboard to view/manage submitted reports; this spec covers only the public-facing capture flow.
- **Authentication**: the reporter is assumed to be an anonymous website visitor (no login required), consistent with "email optional."

---

## Technology Stack

- **Frontend**: JavaScript framework for the website's existing stack (e.g. React) for the widget/modal component — assumed as the standard choice for an interactive website widget.
- **Backend**: REST API (Node.js/Express or equivalent) to receive and persist bug reports, including multipart form handling for screenshot uploads.
- **Database**: Relational database (e.g. PostgreSQL) to store bug report records (category, description, email, screenshot reference, timestamp).
- **File Storage**: Server-side or object storage (e.g. local disk / S3-compatible bucket) for uploaded screenshots, referenced by URL/path in the database.

*(No AI/ML, blockchain, or other specialized technology was requested or implied — none is proposed.)*

---

## Action Plan / Tasks

### Report Widget & Modal
- [ ] Design the "Report a Problem" button/widget placement and visual style.
- [ ] Design the modal layout (category dropdown, description textarea, screenshot upload, email field, submit button, success state).
- [ ] Implement the trigger button/widget on the site shell (visible on all pages).
- [ ] Implement the modal open/close behavior.

### Bug Report Form
- [ ] Build the category dropdown (UI/Design, Functionality, Performance, Other).
- [ ] Build the description textarea with required-field validation.
- [ ] Build optional screenshot upload control with file type/size validation.
- [ ] Build optional email input field with format validation.
- [ ] Wire up "Submit Report" to call the backend API.
- [ ] Display success confirmation message after a successful submission; handle/display error state on failure.

### Backend & Data
- [ ] Design the `bug_reports` database schema (category, description, email, screenshot reference, created_at).
- [ ] Implement `POST /api/bug-reports` endpoint accepting multipart form data.
- [ ] Implement screenshot upload/storage handling and persist the file reference.
- [ ] Add basic input validation and rate limiting on the endpoint.

### QA
- [ ] Write and execute test cases covering: required-field validation, optional-field omission, screenshot upload success/failure, successful submission and success-message display.

---

## Immediate Next Steps

1. Confirm the open questions above (category required?, notification needs, admin/reporting view, upload limits) with the manager.
2. Finalize the modal UI design (Alice) so frontend implementation can start against approved mockups.
3. Stand up the `bug_reports` schema and API contract (Frank/David) so frontend and backend can build in parallel.
4. Implement the widget, modal, and form (Bob/Charlie) against the agreed API contract.
5. QA validates the full end-to-end flow (submission, optional fields, success message) before release.
