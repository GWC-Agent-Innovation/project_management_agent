# Website Bug Report Widget

**Proposed Jira Project Key:** `BRF`

## 1. Project Overview

The Website Bug Report Widget is a lightweight, embeddable feedback tool that lets any visitor to the website report a problem directly from the page they're viewing. It is aimed at general site visitors (no login required) and gives the product/support team a structured, low-friction channel for catching UI, functionality, and performance issues as they happen. The core goal is to replace informal or nonexistent bug-reporting channels with a single "Report a Problem" entry point that captures a categorized description, an optional screenshot, and an optional contact email, so issues can be triaged and followed up on efficiently. This is a small, single-feature scope: one form-based widget backed by a simple storage/API layer.

## 2. Core Requirements

### Functional Requirements

**Entry Point & Modal**
- A "Report a Problem" button/widget must be visible on the website (persistent, accessible from any page).
- Clicking the button opens a modal dialog containing the report form.

**Bug Report Form**
- User can select a bug category from a fixed set: UI/Design, Functionality, Performance, Other.
- User can enter a free-text description of the problem (required).
- User can optionally upload a screenshot image.
- User can optionally enter an email address for follow-up.
- User submits the form via a "Submit Report" button.
- A success message is displayed after successful submission.

### Non-Functional Requirements
- The modal and form must be usable on both desktop and mobile viewport widths (responsive).
- Screenshot uploads should be restricted to common image formats (e.g. PNG/JPG) with a reasonable file-size limit to protect the backend.
- Optional fields (screenshot, email) must not block submission when left empty.
- Submitted reports must be persisted reliably (no silent data loss) so they can be reviewed later.
- Basic form validation (e.g. description required, valid email format if provided) should give the user immediate feedback.

### Assumptions & Open Questions
- No requirement was given for an admin/review interface for submitted reports — this spec assumes reports are stored and viewable directly via the database for now; a dedicated review dashboard is out of scope unless requested separately.
- No authentication/login is implied for the reporting visitor — the widget is intended for anonymous use.
- Screenshot storage mechanism (e.g. local disk vs. object storage) was not specified; the plan assumes server-side file storage with a reference saved in the database.
- No specific browser/device support matrix was given; standard modern browser support is assumed.
- No notification requirement (e.g. emailing the support team on new report) was mentioned — flagged as a possible future enhancement, not included in this scope.

## 3. Technology Stack

- **Frontend:** JavaScript framework component/widget (modal + form), embeddable into the existing website — standard choice for an interactive on-page widget.
- **Backend:** REST API endpoint to receive and persist report submissions, including multipart handling for the optional screenshot upload.
- **Database:** Relational database table (`bug_reports`) to store category, description, optional screenshot reference, optional email, and submission timestamp.
- **File Storage:** Server-side storage for uploaded screenshots, referenced by path/URL in the database record.

*(Only the technologies implied directly by the requirements — a form widget, an API to receive it, and a database to store it — are included; no specialized stacks such as AI/ML or blockchain are warranted here.)*

## 4. Action Plan / Tasks

### Report Entry Point & Modal
- [ ] Design the "Report a Problem" button/widget and modal UI/UX
- [ ] Implement the button/widget and wire it up to open the modal on click

### Bug Report Form
- [ ] Build the form: category dropdown (UI/Design, Functionality, Performance, Other), description textarea, optional screenshot upload input, optional email input
- [ ] Add client-side validation and display a success message after submission

### Backend & Storage
- [ ] Design the `bug_reports` database schema (category, description, screenshot reference, email, timestamp)
- [ ] Build the `POST /api/bug-reports` endpoint, including screenshot upload handling and persistence

### QA
- [ ] Write and execute test cases covering all categories, optional-field combinations, and the success-message flow

## 5. Immediate Next Steps

1. Finalize the UI/UX mockup for the "Report a Problem" button and modal (Alice).
2. Implement the button/widget and modal shell on the frontend (Bob).
3. Design and confirm the `bug_reports` database schema (Frank).
4. Build the backend submission endpoint with screenshot upload support (David).
5. Build out the form fields, validation, and success-message UX, then hand off for QA testing (Charlie → Grace).
