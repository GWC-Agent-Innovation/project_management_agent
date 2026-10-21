# Customer Feedback Widget (CFW)

**Jira Project Key**: `CFW`

## Project Overview

The Customer Feedback Widget (CFW) is a lightweight, embeddable feedback tool for the company website. It lets visitors quickly rate their experience (1–5 stars) and leave optional comments through a simple modal, without navigating away from the page they're on. Internally, an admin screen allows staff to review, filter, and act on submitted feedback. The goal is to give the business a low-friction channel for collecting customer sentiment and a simple internal tool to monitor it, with minimal footprint on page performance and minimal engineering overhead to maintain.

## Core Requirements

### Functional Requirements

**User Feedback Form (Widget)**
- Display a modal/dialog that visitors can open from the website to submit feedback.
- Capture a star rating from 1 to 5 (required field).
- Capture an optional free-text comment.
- Submit the rating + comment to the backend and confirm successful submission to the user (e.g. "Thank you" state).
- Basic client-side validation (rating must be selected before submit).

**Admin Feedback List (Admin Screen)**
- Authenticated admin view listing all submitted feedback entries (rating, comment, submission date/time).
- Ability to filter the list — at minimum by star rating and by date range.
- Paginated or scrollable list to handle growing volumes of feedback.

### Non-Functional Requirements
- Widget must be lightweight and must not noticeably impact host page load time.
- Widget should be embeddable on any page of the website (reusable component/script).
- Admin screen must be access-restricted (authenticated/authorized staff only).
- Feedback data persisted reliably in a database with timestamps.
- Basic responsive design for both the widget (mobile + desktop visitors) and the admin screen (desktop-first, staff use).

### Assumptions & Open Questions
- **Authentication for Admin screen**: The requirements do not specify how admins log in. Assumption: a simple existing/basic authentication mechanism will gate the admin screen; exact auth provider (internal SSO vs. simple login) is an open question for the client.
- **Anonymity**: No requirement was given for capturing visitor identity (name/email). Assumption: feedback is anonymous unless stated otherwise.
- **Volume/Scale**: No expected traffic/volume was provided. Assumed low-to-moderate volume suitable for a lightweight widget; not designed for high-throughput analytics at this stage.
- **Export/Reporting**: Not mentioned — out of scope for this phase unless the client requests it later.
- **Notifications** (e.g. email/Slack alert on new feedback): Not mentioned — out of scope for this phase.

## Technology Stack

- **Frontend**: JavaScript/React-based embeddable widget component (modal UI) + a small React-based admin screen.
- **Backend**: REST API (Node.js/Express or equivalent) to receive and serve feedback data.
- **Database**: Relational database (e.g. PostgreSQL) to persist feedback entries with rating, comment, and timestamp.
- **Auth**: Basic authenticated route/session guard for the admin screen.
- **Hosting/Delivery**: Widget delivered as an embeddable script/component; standard web hosting for the admin screen and API.

*(Only technologies explicitly implied by "website widget + admin screen" are listed; no specialized stacks such as AI/ML or blockchain are warranted here.)*

## Action Plan / Tasks

### User Feedback Form (Widget)
- [ ] Design modal UI (star rating control + comment textarea + submit button)
- [ ] Build reusable/embeddable widget component
- [ ] Implement client-side validation (rating required)
- [ ] Build `POST /feedback` API endpoint
- [ ] Create `feedback` database table/schema
- [ ] Show success/confirmation state after submission

### Admin Feedback List (Admin Screen)
- [ ] Design admin list UI (table/list with rating, comment, date)
- [ ] Build `GET /feedback` API endpoint with filter query params (rating, date range)
- [ ] Build admin screen frontend with filter controls
- [ ] Add auth guard to restrict admin screen access

## Immediate Next Steps
1. Confirm admin authentication approach with the client (existing login system vs. new simple auth).
2. Set up the database schema for `feedback` entries (rating, comment, created_at).
3. Build the `POST /feedback` endpoint and the feedback modal widget end-to-end first (highest-value path for visitors).
4. Build the `GET /feedback` endpoint with filtering, then the admin list screen consuming it.
5. QA pass on widget embedding (cross-page) and admin filter behavior before release.
