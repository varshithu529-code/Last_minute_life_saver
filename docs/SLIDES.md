# Last Minute Life Saver — Complete Slide Content
**Copy each slide directly into PowerPoint / Google Slides**

---

## SLIDE 1 — Title

**Title:** Last Minute Life Saver

**Subtitle:** Autonomous Productivity Companion

**Tagline (large text):**
This bot doesn't just remind you — it saves you.

**Footer:**
- Google Hackathon 2026
- Team: [Your Name(s)]
- GitHub: [your-repo-url]

**What to say (30 sec):**
"Hi, we're Last Minute Life Saver — an autonomous productivity companion. Most tools remind you what's wrong. We detect problems and fix them before you even ask."

---

## SLIDE 2 — The Problem

**Title:** The Problem — Reminders Aren't Enough

**Subtitle:** Knowledge workers spend hours on reactive firefighting

**Bullet 1 — Calendar chaos**
- Double-bookings discovered minutes before the meeting
- Manual rescheduling across Outlook, Google Calendar, and Teams

**Bullet 2 — Deadline slips**
- Overdue tasks pile up; users write apology emails from scratch
- No proactive extension requests — just stress and missed commitments

**Bullet 3 — Meeting unpreparedness**
- Last meeting notes live in email, Slack, or nowhere
- Walk into board reviews and client syncs without context

**Bullet 4 — Tool fatigue**
- Calendars notify. Task apps notify. Email notifies.
- None of them **act** on your behalf

**Quote (callout box):**
"I'm not forgetful — I'm overloaded. I need something that saves me at the last minute."

**What to say (45 sec):**
"Every day, professionals juggle conflicts, deadlines, and meetings. Existing tools tell you something is wrong — but you're still the one doing the work. That's the gap we set out to close."

---

## SLIDE 3 — Our Solution

**Title:** Our Solution — Proactive AI That Acts

**Subtitle:** Last Minute Life Saver: detect → decide → intervene

**Feature 1 — Conflict rescue**
Automatically detects overlapping meetings and reschedules them via calendar API

**Feature 2 — Deadline rescue**
Finds overdue and approaching tasks; drafts professional extension emails

**Feature 3 — Meeting prep assistant**
Surfaces prior notes and generates a prep checklist before high-stakes meetings

**Feature 4 — Full transparency**
Every action logged with confidence scores — auditable, not a black box

**Call to action (bold):**
One message in chat → "Save my day" → bot handles the rest

**What to say (30 sec):**
"We built an agent that doesn't wait for you to dig through your calendar. It scans your schedule and tasks, takes action, and shows you exactly what it did — with the option to confirm or undo."

---

## SLIDE 4 — User Experience (Wireframe)

**Title:** Chat-First Experience

**Subtitle:** Natural language in → proactive actions out

**Left column — User types:**
- "Rescue my deadline"
- "Prep me for meeting"
- "Resolve conflict"
- "Save my day"

**Right column — Bot responds:**
"I noticed your expense report is overdue. I've drafted an extension email to your manager — want me to send it?"

**Bottom — Dynamic action cards:**

| Card | Title | Action | Buttons |
|------|-------|--------|---------|
| Conflict | Meeting Conflict Detected | Rescheduled to tomorrow 10 AM | Undo · Confirm |
| Deadline | Expense Report Due Soon | Drafted extension email | Preview · Send |
| Prep | Meeting Prep — Q2 Board Review | Last notes + checklist ready | Open Notes |

**Top bar — Impact metrics:**
Conflicts Resolved: 3 · Deadlines Rescued: 2 · Meetings Prepped: 4 · Focus Score: 85/100 · Streak: 5 days

**What to say (live demo 60 sec):**
"Let me show you. I type 'Rescue my deadline' — the bot replies in natural language and action cards appear below. I can preview the email, confirm a reschedule, or open meeting notes. Metrics update in real time."

---

## SLIDE 5 — Architecture

**Title:** System Architecture

**Subtitle:** API-first, modular, agent-centric

**Diagram (center):**
```
┌─────────────┐     REST /v1     ┌─────────────────────────────┐
│  React UI   │ ◄────────────► │  FastAPI Backend            │
│  Chat+Cards │                  │  Tasks · Events · Agent API │
└─────────────┘                  └──────────────┬──────────────┘
                                                │
                                   ┌────────────▼────────────┐
                                   │  LangGraph Agent        │
                                   │  StateGraph + routing   │
                                   └────────────┬────────────┘
                          ┌─────────────────────┼─────────────────────┐
                          ▼                     ▼                     ▼
                   LangChain LLM          Calendar API           SQLite DB
                   (GPT-4o)               (Outlook/Google)       + Redis
```

**Four layers (bullets):**
1. **Frontend** — React + Vite: chat entry, action cards, impact metrics
2. **Backend** — FastAPI with versioned REST endpoints (/v1/tasks, /v1/agent)
3. **Agent** — LangGraph orchestrates multi-step rescue workflow
4. **Data** — SQLite for POC; schema ready for PostgreSQL migration

**What to say (30 sec):**
"Clean separation: the UI talks to a stateless API. The API invokes a LangGraph agent. Tools handle calendar, database, and LLM calls. Everything is logged and testable."

---

## SLIDE 6 — LangGraph Agent Workflow

**Title:** Agent Brain — LangGraph State Machine

**Subtitle:** Explicit workflow, not a chat loop

**Flow diagram:**
```
START
  │
  ▼
detect_conflicts ──no conflicts──► deadline_rescue
  │
  yes
  ▼
propose_reschedule
  │
  ▼
execute_reschedule (auto)
  │
  ▼
deadline_rescue ──► missed + approaching emails drafted
  │
  ▼
meeting_prep ──► notes + checklist generated
  │
  ▼
finalize ──► narrative + action cards + summary
  │
 END
```

**Why LangGraph (3 bullets):**
- **Conditional routing** — skip reschedule if no conflicts
- **Shared state** — each node reads/writes AgentState (conflicts, rescues, prep)
- **Auditable** — every node transition maps to a logged agent action

**What to say (30 sec):**
"We chose LangGraph over a simple prompt chain because productivity rescue is a multi-step workflow with branches. Conflict found? Reschedule. No conflict? Jump to deadlines. The graph makes this explicit and debuggable."

---

## SLIDE 7 — Demo Data & Scenarios

**Title:** Realistic Demo — 30 Days of Synthetic Data

**Subtitle:** Guaranteed scenarios for live pitch (no real PII)

**Scenario 1 — Double-booking**
- Client sync + Architecture review overlap tomorrow at 10 AM
- Agent: detects → proposes → auto-executes reschedule

**Scenario 2 — Missed deadlines**
- Expense report (2 days overdue)
- Security audit checklist (6 hours overdue)
- Agent: drafts apology + extension recovery emails

**Scenario 3 — Approaching deadlines**
- Q2 presentation deck (due in 20 hours)
- Critical checkout bug (due in 8 hours)
- Agent: drafts proactive extension requests

**Scenario 4 — Meeting prep**
- Q2 Board Review in ~3 hours with prior notes in system
- Agent: surfaces last meeting notes + LLM prep checklist

**Footer:**
61 tasks · 14 events · 4 habits · Seeded via `seed_synthetic_data.py`

**What to say (20 sec):**
"We seed a full month of realistic data plus guaranteed crisis scenarios so the demo always works — safely, with no real user data."

---

## SLIDE 8 — Tech Stack

**Title:** Technology Stack

**Subtitle:** Production-minded choices for a hackathon POC

| Component | Technology | Why |
|-----------|------------|-----|
| Agent orchestration | LangGraph | Stateful multi-step workflows |
| LLM layer | LangChain + Azure OpenAI GPT-4o | Guardrails, retries, Azure-ready |
| Backend API | FastAPI + Python 3.11 | Fast, typed, auto OpenAPI docs |
| Frontend | React + Vite | Chat wireframe, action cards |
| Database | SQLite → PostgreSQL | POC now, migrate later |
| Cache | Redis (optional) | Task prioritization scores |
| Calendar | Microsoft Graph + Google Calendar | OAuth2 stubs in place |
| Task scoring | Eisenhower Matrix + ML composite | Urgency × importance ranking |
| CI/CD | GitHub Actions | Lint, test, build on every push |
| Testing | PyTest (7 tests) + Jest | API + component coverage |

**What to say (20 sec):**
"LangGraph and LangChain are the core differentiators. Everything else — FastAPI, React, SQLite — supports a fast, demo-ready POC that scales to production."

---

## SLIDE 9 — Guardrails & Trust

**Title:** Guardrails — Safe Autonomous Actions

**Subtitle:** We act proactively, but never recklessly

**Guardrail 1 — LLM confidence scoring**
Heuristic score on every response. Below threshold → warning appended: "Please verify before acting."

**Guardrail 2 — Input sanitization**
All user chat and task input escaped and length-limited before processing.

**Guardrail 3 — Rate limiting**
API rate limits prevent abuse (slowapi on task creation).

**Guardrail 4 — Graceful degradation**
Works fully in offline mode without API key — deterministic fallback responses.

**Guardrail 5 — Audit trail**
Every agent action stored in `agent_logs`: type, description, confidence, timestamp.

**Guardrail 6 — Synthetic sandbox**
Demo uses fake data only — no real PII, emails, or calendar accounts required.

**What to say (30 sec):**
"Autonomous doesn't mean uncontrolled. Every LLM output gets a confidence score. Every action is logged. Confirm/Undo buttons keep the human in the loop for sends and reschedules."

---

## SLIDE 10 — Impact & Before/After

**Title:** Measurable Impact

**Subtitle:** Gamification shows value at a glance

**Metrics dashboard (large numbers):**
- 3 Conflicts Resolved
- 2 Deadlines Rescued
- 4 Meetings Prepped
- 85/100 Focus Score
- 5-day Rescue Streak

**Before vs After table:**

| Situation | Before (typical tools) | After (Last Minute Life Saver) |
|-----------|------------------------|--------------------------------|
| Double-booked | Calendar sends alert | Bot reschedules automatically |
| Overdue task | Red badge in task app | Bot drafts recovery email |
| Meeting in 3 hours | Search email for notes | Bot delivers notes + checklist |
| End of day | User triages manually | Bot ran full rescue workflow |

**What to say (20 sec):**
"We track what the bot saves you — not just what it reminds you about. Focus score and streak gamify the habit of letting the agent handle firefighting."

---

## SLIDE 11 — Roadmap

**Title:** What's Next — Path to Production

**Subtitle:** From hackathon POC to enterprise deployment

**Phase 1 — Integrations (Q2)**
- Live OAuth2 for Microsoft Graph + Google Calendar
- Trello / Jira as real task sources

**Phase 2 — Enterprise hardening (Q3)**
- PostgreSQL + Redis in production
- Human-in-the-loop approval before send/reschedule
- Role-based access and multi-user support

**Phase 3 — Channels (Q4)**
- Azure Speech SDK — voice interface ("Rescue my deadline" by voice)
- Microsoft Copilot Studio deployment
- Mobile push for proactive interventions

**What to say (20 sec):**
"This POC proves the agent workflow. Production adds live calendar sync, approval gates, and voice — same LangGraph core, hardened for enterprise."

---

## SLIDE 12 — Close & Q&A

**Title:** Last Minute Life Saver

**Subtitle (large):**
Reminders tell you what's wrong.
Last Minute Life Saver fixes it — autonomously.

**Three takeaways:**
1. **Proactive** — detects conflicts, deadlines, and prep gaps automatically
2. **Agentic** — LangGraph workflow, not a chatbot wrapper
3. **Trustworthy** — confidence scores, audit logs, confirm/undo controls

**Links:**
- Demo: http://localhost:5173
- API: http://localhost:8000/docs
- Repo: [your-repo-url]

**Closing line:**
"Thank you. We'd love your questions — or try 'Save my day' on the demo."

---

# APPENDIX SLIDE A — API Overview (if asked)

**Title:** API Endpoints (v1)

- `POST /v1/chat` — Intent-driven chat → action cards
- `POST /v1/agent/run` — Full LangGraph workflow
- `GET /v1/agent/metrics` — Impact + gamification
- `GET /v1/agent/conflicts` — Detect double-bookings
- `GET /v1/agent/deadline-rescue` — Draft rescue emails
- `GET /v1/tasks?prioritize=true` — Eisenhower-ranked tasks
- `GET /v1/events` — Calendar with conflict flags

---

# APPENDIX SLIDE B — Task Prioritization (if asked)

**Title:** Eisenhower Matrix + ML Scoring

**Urgency score (0–1):** Based on hours until due date
- Overdue → 1.0 · Due in 24h → 0.9 · Due in 72h → 0.7

**Importance score (0–1):** Keyword heuristics + estimated effort
- "client", "deadline", "critical" boost score

**Composite ML score:** 0.55 × urgency + 0.45 × importance

**Quadrants:** Do First · Schedule · Delegate · Eliminate

---

# FULL SPEAKER SCRIPT (3 minutes)

**[Slide 1 — 15 sec]**
"Hi, we're Last Minute Life Saver. Our tagline says it all: this bot doesn't just remind you — it saves you."

**[Slide 2 — 30 sec]**
"Here's the problem. Professionals deal with double-bookings, slipping deadlines, and meetings they're not prepared for. Calendars and task apps send notifications — but you're still the one fixing everything. That's reactive firefighting, and it costs hours every week."

**[Slide 3 — 20 sec]**
"Our solution is an autonomous agent that detects these problems and intervenes — rescheduling conflicts, drafting deadline emails, and prepping you for meetings — all logged with confidence scores."

**[Slide 4 — LIVE DEMO 60 sec]**
"Let me show you. [Open localhost:5173] I type 'Rescue my deadline.' The bot responds: 'I noticed your expense report is overdue — I've drafted an extension email, want me to send it?' Action cards appear — I can preview the email, confirm a reschedule, or open meeting notes. Metrics update at the top."

**[Slide 5–6 — 40 sec]**
"Under the hood: React frontend, FastAPI backend, and a LangGraph state machine. The agent graph routes through conflict detection, reschedule, deadline rescue, and meeting prep — with conditional branches, not a single chat prompt."

**[Slide 9 — 20 sec]**
"We built in guardrails: confidence scoring on every LLM output, full audit logging, input sanitization, and confirm/undo buttons so humans stay in control."

**[Slide 12 — 15 sec]**
"Reminders tell you what's wrong. Last Minute Life Saver fixes it — autonomously. Thank you — questions?"

---

# VISUAL ASSETS TO ADD

1. **Slide 4:** Screenshot of Home page (chat + cards + metrics)
2. **Slide 5:** Architecture diagram (from README)
3. **Slide 6:** LangGraph flowchart (from README)
4. **Slide 10:** Screenshot of metrics after "Save my day"
5. **Logo/icon:** ⚡ lightning bolt (matches app sidebar)

**Color palette:**
- Background: #0F1419
- Surface: #1A2332
- Accent: #3B82F6
- Success: #22C55E
- Warning: #F59E0B
- Danger: #EF4444
