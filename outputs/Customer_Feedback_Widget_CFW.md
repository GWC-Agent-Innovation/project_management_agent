# Customer Feedback Widget (CFW)

**Jira Project Key:** `CFW`

## Project Overview

The Customer Feedback Widget (CFW) is a lightweight, embeddable feedback tool for the client's website. It allows visitors to submit a quick rating (1-5 stars) and optional comments through a modal, and gives internal administrators a dedicated screen to view, filter, and export that feedback as CSV for further analysis. The goal is to give the business a fast, low-friction way to capture voice-of-customer signals directly on the site and turn them into actionable, exportable data without needing a heavyweight survey platform. The scope, as provided, is intentionally narrow: one visitor-facing capture form and one admin review/export screen.

## Core Requirements

### Functional Requirements

**Feedback Capture (Visitor-Facing)**
- Display a modal/dialog that visitors can open to submit feedback.
- Modal includes a 1-5 star rating control (required).
- Modal includes a free-text comments field (optional).
- Submitting the form persists the feedback record (rating, comment, timestamp, and page/source context) to the backend.
- Basic client-side validation (e.g., a rating must be selected before submit).
- Confirmation state/message shown to the visitor after successful submission.

**Admin Feedback Management**
- Admin-only screen listing all submitted feedback entries (rating, comment, submission date/time).
- Filtering support on the list (e.g., by rating value and/or date range).
- Export the currently filtered (or full) list to a CSV file.
- Basic pagination or scrolling for the list to handle a growing volume of feedback.

### Non-Functional Requirements

- **Lightweight**: the widget (modal + trigger) should load quickly and not noticeably impact host page performance.
- **Embeddable**: the widget must be easily integrated into the existing website (e.g., a script/component drop-in) without a full page reload.
- **Security**: the admin feedback list must be restricted to authenticated administrators only.
- **Usability**: the star rating control and modal must be intuitive and accessible (keyboard operable, screen-reader friendly).
- **Data integrity**: CSV export must accurately reflect the filtered data set at the time of export.
- **Browser compatibility**: widget must function on current major browsers (Chrome, Firefox, Safari, Edge).

### Assumptions & Open Questions

- No authentication/authorization mechanism was specified for the admin screen — this document assumes a simple admin login (username/password) is needed. **Open question**: does the client already have an admin auth system this should plug into?
- No specific filter fields were named beyond "filter" — this document assumes filtering by star rating and by submission date range as the most common baseline. **Open question**: are there additional filter needs (e.g., by page URL, by keyword in comments)?
- No volume/scale expectations were given (e.g., expected submissions per day). Assumed low-to-moderate volume suitable for a single relational database table.
- No design/branding assets were mentioned; assumed the UI/UX Designer will produce a simple, on-brand modal and admin table design.
- Hosting/deployment environment for the widget script and admin app was not specified; assumed a standard web app deployment (frontend + backend API + database) with CI/CD.

## Technology Stack

| Layer | Choice | Rationale |
|---|---|---|
| Frontend (Widget + Admin UI) | React | Standard choice for an embeddable modal widget and an admin SPA; not explicitly stated but the obvious fit for a modern website widget. |
| Backend API | Node.js (Express) | Standard lightweight REST API to receive feedback submissions and serve the admin list/export endpoints. |
| Database | PostgreSQL | Relational store well suited to structured feedback records (rating, comment, timestamp) and simple filtering queries. |
| Auth (Admin) | Session/JWT-based auth | Simple, standard mechanism to gate the admin screen. |
| CSV Export | Server-side CSV generation | Ensures exported data matches applied filters exactly. |
| CI/CD | GitHub Actions (or equivalent) | Standard pipeline for build/test/deploy of a small web app. |

## Action Plan / Tasks

### User Feedback Form (Modal)
- [ ] Design modal UI (star rating control + comment textarea) — Alice
- [ ] Build modal component with open/close trigger — Bob/Charlie
- [ ] Implement 1-5 star rating input component — Bob/Charlie
- [ ] Add client-side validation (rating required) — Bob/Charlie
- [ ] Build `POST /feedback` API endpoint — David/Emily
- [ ] Design `feedback` DB table (rating, comment, timestamp, source) — Frank
- [ ] Show success/confirmation state after submit — Bob/Charlie
- [ ] QA: form validation, submission, and confirmation flow — Grace/Henry

### Admin Feedback List
- [ ] Design admin list/table UI with filter controls — Alice
- [ ] Build admin login/auth flow — David/Emily
- [ ] Build `GET /feedback` API with filter query params — David/Emily
- [ ] Build admin list screen (table, pagination, filters) — Bob/Charlie
- [ ] Build `GET /feedback/export` CSV export endpoint — David/Emily
- [ ] Wire up "Export to CSV" button in admin UI — Bob/Charlie
- [ ] QA: filtering accuracy and CSV export correctness — Grace/Henry

### Platform / Cross-Cutting
- [ ] Set up project repo, environments, and CI/CD pipeline — Ivy
- [ ] Provision PostgreSQL database and connection config — Frank/Ivy
- [ ] Set up staging deployment for stakeholder review — Ivy

## Immediate Next Steps

1. Finalize the admin authentication approach with the client (standalone login vs. existing system).
2. Alice to produce quick mockups for the feedback modal and the admin list screen.
3. Frank to finalize the `feedback` table schema (fields, indexes for filtering).
4. David/Emily to scaffold the API (`POST /feedback`, `GET /feedback`, `GET /feedback/export`).
5. Ivy to set up the repo, CI/CD, and staging environment so early builds can be reviewed continuously.
