# Customer Feedback Widget (CFW)

**Jira Project Key:** `CFW`

## Project Overview

The Customer Feedback Widget (CFW) is a lightweight, embeddable feedback tool for the company website that lets visitors quickly rate their experience and leave comments without leaving the page they're on. The widget surfaces as a modal containing a 1-5 star rating control and a free-text comment field. Submitted feedback is stored centrally and made available to internal staff through a simple admin screen where entries can be viewed and filtered. The goal is to give the business a fast, low-friction channel for capturing visitor sentiment and a straightforward way for admins to review that feedback, with minimal engineering overhead and no impact on site performance.

## Core Requirements

### Functional Requirements

**Feedback Capture (Visitor-Facing)**
- Display a modal on the website that visitors can open to submit feedback.
- Modal contains a 1-5 star rating control (required).
- Modal contains a free-text comments field (optional).
- Submitting the form sends the rating and comment to the backend and confirms receipt to the visitor.
- Basic client-side validation (e.g., a rating must be selected before submission).

**Admin Feedback Management**
- Admin screen listing all submitted feedback entries (rating, comment, submission date/time).
- Ability to filter the list (e.g., by star rating and/or date range).
- Read-only view for this phase — no requirement stated for editing or deleting entries.

### Non-Functional Requirements

- The widget must be lightweight and embeddable without materially affecting host page load performance.
- Feedback data must persist reliably (no data loss on submission).
- Admin screen should only be accessible to authorized staff (basic access control assumed, see Open Questions).

### Assumptions & Open Questions

- **Authentication for the admin screen** was not specified — this plan assumes a simple authenticated admin login is required and includes it as an implicit baseline task, since an unsecured admin view of user-submitted data would not be acceptable practice. Please confirm expected access model (internal-only? role-based?).
- **Embedding mechanism** (script tag/snippet vs. iframe vs. framework component) was not specified; a standard embeddable JavaScript snippet is assumed.
- **Volume/scale expectations** for feedback submissions were not provided; no specific performance target has been set beyond "lightweight."
- **Notifications** (e.g., email/Slack alert on new feedback) were not requested and are out of scope unless confirmed otherwise.
- **Editing/exporting/deleting feedback entries** from the admin screen was not requested and is treated as out of scope for this phase.

## Technology Stack

- **Frontend (Widget):** Vanilla JavaScript embeddable modal component (framework-agnostic to keep footprint light on host pages)
- **Frontend (Admin Screen):** React (standard choice for an internal data-management UI)
- **Backend:** Node.js / Express REST API
- **Database:** PostgreSQL (structured storage for rating + comment + timestamp records)
- **Hosting/Infra:** Standard web hosting with basic CI/CD pipeline for the API and admin app

## Action Plan / Tasks

### Feedback Modal (Visitor Widget)
- [ ] Design modal UI (star rating control + comment textarea) with Alice Johnson's UX input
- [ ] Build embeddable modal component
- [ ] Add client-side validation (rating required before submit)
- [ ] Wire submit action to backend API with success/error confirmation

### Feedback Submission API & Storage
- [ ] Design database schema for feedback entries (rating, comment, timestamp)
- [ ] Build `POST /api/feedback` endpoint with validation
- [ ] Write automated/QA test cases for the submission flow

### Admin Feedback List Screen
- [ ] Design admin list layout with filter controls
- [ ] Build admin table UI (list view + filters for rating/date)
- [ ] Build `GET /api/feedback` endpoint supporting filter/query parameters
- [ ] Confirm and implement basic admin access control

### Immediate Next Steps
1. Confirm the admin access-control model (auth requirement) with the client before backend work begins.
2. Finalize the embeddable widget approach (script snippet) and confirm target pages for embedding.
3. Design and review the database schema for feedback entries with the Database Engineer.
4. Build the feedback modal UI in parallel with the submission API.
5. Build the admin list screen once the underlying feedback data model is confirmed.
