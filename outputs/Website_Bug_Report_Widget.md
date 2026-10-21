# Website Bug Report Widget

**Proposed Jira Project Key:** `BUGR`

## 1. Project Overview

GWC's website currently has no built-in way for visitors to report problems they encounter while browsing. This project delivers a lightweight, always-available **"Report a Problem"** widget that opens a modal form, letting any visitor categorize an issue, describe it, optionally attach a screenshot, and optionally leave contact details for follow-up. The goal is to give the team a low-friction channel for capturing real-world bugs and UX issues directly from the people experiencing them, without requiring visitors to leave the site, sign in, or use a separate support tool. On submission, the visitor sees an immediate confirmation, and the report is persisted on the backend for the team to triage later.

## 2. Core Requirements

### Functional Requirements

**Report Widget & Modal**
- A "Report a Problem" button/widget must be visible on the website (persistent, accessible from any page).
- Clicking the button opens a modal containing the report form.

**Report Form**
- User can select a bug category from a fixed list: `UI/Design`, `Functionality`, `Performance`, `Other`.
- User can enter a free-text description of the problem (required).
- User can optionally upload a screenshot image.
- User can optionally enter an email address for follow-up.
- User submits the form via a "Submit Report" action.

**Submission Handling**
- On successful submission, the system stores the report (category, description, screenshot if provided, email if provided, timestamp).
- User is shown a clear success message after submission.
- User is shown an error message if submission fails (e.g., network/server error).

### Non-Functional Requirements
- The widget must not interfere with normal site navigation or layout (should be unobtrusive, e.g. floating button).
- Description and category fields are required; screenshot and email are optional — the form must submit successfully without them.
- Screenshot uploads should be restricted to common image formats and a reasonable max file size.
- Submitted data must be safely persisted (no data loss on successful submit) and stored in a way the team can review later.
- Basic form validation must run client-side before submission (e.g., category and description required).

### Assumptions & Open Questions
- No mention of where submitted reports are viewed/managed (e.g., an internal admin dashboard) — assumed **out of scope** for this iteration; reports will be stored and made available via the database/API for now.
- No authentication is implied for the reporting visitor — the form is intended for anonymous/public use.
- Max screenshot file size and accepted formats were not specified — will default to common web standards (e.g., JPG/PNG/GIF, up to ~5MB) unless the manager specifies otherwise.
- No specific browser/device support matrix was given — assumed standard modern desktop and mobile browsers.

## 3. Technology Stack

- **Frontend:** JavaScript-based framework (React) for the widget/modal component, embeddable across existing website pages.
- **Backend:** REST API (Node.js/Express) to receive and validate submissions.
- **Database:** Relational database (e.g., PostgreSQL) to persist bug reports.
- **File Storage:** Server/object storage for uploaded screenshots (referenced by URL from the database record).
- **Testing:** Manual + scripted QA test cases for the end-to-end submission flow.

*(Stack choices reflect standard tooling for a public-facing web form + API + storage; no specific stack was dictated in the requirements.)*

## 4. Action Plan / Tasks

### Report Widget & Modal (Frontend)
- [ ] Build the persistent "Report a Problem" floating button/widget
- [ ] Build the modal component that opens on click
- [ ] Build category dropdown (UI/Design, Functionality, Performance, Other)
- [ ] Build description textarea (required)
- [ ] Build optional screenshot upload control
- [ ] Build optional email input field

### Submission Flow (Frontend)
- [ ] Implement client-side validation (required fields)
- [ ] Wire "Submit Report" to call the backend API
- [ ] Display success message on successful submission
- [ ] Display error message on failed submission

### Backend & Storage
- [ ] Design `bug_reports` database schema (category, description, screenshot_url, email, created_at)
- [ ] Implement `POST /api/bug-reports` endpoint (accepts multipart form data)
- [ ] Implement screenshot file storage and validation (type/size)
- [ ] Return success/error responses to the frontend

### Quality Assurance
- [ ] Write test cases covering required/optional fields, screenshot upload, and success/error states
- [ ] Execute end-to-end testing of the full report submission flow

## 5. Immediate Next Steps

1. Confirm the Jira project key (`BUGR` proposed) and get manager approval to create the board.
2. Build the "Report a Problem" button/widget and modal UI (frontend).
3. Stand up the `bug_reports` database schema and the submission API endpoint (backend).
4. Wire the frontend form to the API, including client-side validation and success/error messaging.
5. QA the full flow end-to-end (required/optional fields, screenshot upload, success confirmation) before release.
