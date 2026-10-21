# Customer Feedback Widget (CFW)
**Jira Project Key:** `CFW`

## Project Overview
The Customer Feedback Widget (CFW) is a lightweight, embeddable feedback tool for the company website that lets visitors quickly rate their experience (1–5 stars) and leave a comment through a simple modal. Submitted feedback is captured and stored so that internal staff can review it through a dedicated admin screen, which supports viewing and filtering entries. The goal is to give the business a fast, low-friction channel for collecting customer sentiment without building a full survey platform — just a focused widget plus a minimal internal review tool. This is a small, tightly-scoped project consisting of two core capabilities: the visitor-facing feedback form and the admin feedback list.

## Core Requirements

### Functional Requirements
**Feedback Capture (Visitor-facing)**
- Display a modal/dialog on the website that visitors can open to submit feedback.
- Allow selection of a star rating from 1 to 5.
- Allow entry of free-text comments alongside the rating.
- Validate that a rating is selected before allowing submission (comment can be optional unless clarified otherwise — see Open Questions).
- Persist each submission (rating, comment, timestamp) to a backend data store via an API call.

**Admin Feedback Management**
- Provide an admin-only screen listing all submitted feedback entries.
- Display key fields per entry: rating, comment, and submission date/time.
- Allow filtering of the feedback list (e.g., by star rating and/or date range).
- Support basic pagination or scrolling for larger volumes of feedback (assumption — see below).

### Non-Functional Requirements
- **Lightweight**: the widget should load quickly and not noticeably impact page performance (client explicitly asked for a "lightweight" widget).
- **Responsive UI**: modal and admin list should render correctly on common desktop and mobile viewport sizes.
- **Basic access control**: the admin feedback list should only be reachable by authorized/admin users (assumption, since it's described as an "admin screen").
- **Data integrity**: submitted ratings must be constrained to the 1–5 range at both client and server level.

### Assumptions & Open Questions
- **Authentication for admin screen**: The requirements say "admin screen" but do not specify how admin access is secured (existing auth system, new login, IP restriction, etc.). Assumed a basic authenticated/admin-gated route for now — needs confirmation.
- **Comment required or optional**: Not specified whether a comment is mandatory alongside the rating. Assumed optional, rating is mandatory.
- **Anonymous vs. identified feedback**: No mention of capturing visitor identity/email — assumed fully anonymous submissions for v1.
- **Filter fields**: The requirement only says "filter submitted feedback entries" without specifying which fields. Assumed filtering by star rating and date range as the most common/expected filters — should be confirmed with the client.
- **Embedding mechanism**: Not specified whether the widget is a JS snippet embedded on arbitrary pages or a component within an existing site codebase. Assumed it will be integrated directly into the existing website's frontend for v1.
- **Volume/scale**: No expected traffic or feedback volume was given; no specific performance targets are defined beyond "lightweight."

## Technology Stack
- **Frontend**: React (component-based modal widget + admin list UI)
- **Backend**: Node.js / Express REST API (standard, lightweight choice matching a simple widget + admin screen use case)
- **Database**: PostgreSQL (relational storage for structured feedback entries: rating, comment, timestamp)
- **Hosting/Infra**: Standard web hosting integrated with the existing company website; CI/CD pipeline for deployment
- **Testing**: Manual + basic automated QA validation of form submission and admin filtering flows

*Note: No specific frontend/backend technologies were named in the source requirements. The above reflects the standard, minimal stack appropriate for a small widget + admin list application; adjust if the client's existing website already uses a specific stack.*

## Action Plan / Tasks

### Feedback Modal (Visitor-Facing)
- [ ] Design modal UI/UX: star rating selector + comment textarea
- [ ] Build modal component (open/close behavior, responsive layout)
- [ ] Implement client-side validation (rating required, comment optional)
- [ ] Wire submission to backend API

### Feedback Submission Backend
- [ ] Design database schema for feedback entries (id, rating, comment, created_at)
- [ ] Implement `POST /api/feedback` endpoint with server-side validation
- [ ] Add error handling and confirmation response to the widget

### Admin Feedback List Page
- [ ] Build admin list UI (table/list view of feedback entries)
- [ ] Implement `GET /api/feedback` endpoint (with pagination support)
- [ ] Display rating, comment, and timestamp per entry

### Admin Filtering
- [ ] Add filter controls (by rating, by date range) to the admin UI
- [ ] Implement backend query filtering support in the feedback API
- [ ] Validate filtered results render correctly for edge cases (no results, single result)

## Immediate Next Steps
1. Confirm open questions with the client: admin auth approach, required vs. optional comment, and exact filter fields.
2. Finalize and lock the database schema for feedback entries.
3. Build the feedback modal UI and connect it to a stubbed/mock submission endpoint to unblock parallel frontend/backend work.
4. Stand up the real `POST /api/feedback` and `GET /api/feedback` endpoints against the finalized schema.
5. Build the admin list screen and layer in filtering once the base list view is functional.
