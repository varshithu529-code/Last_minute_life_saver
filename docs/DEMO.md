# Pitch Demo Script

> **"This bot doesn't just remind you — it saves you."**

## Before the demo (2 min)

```powershell
cd backend
.\.venv\Scripts\activate
python scripts/seed_synthetic_data.py
uvicorn app.main:app --reload --port 8000
```

```powershell
cd frontend
npm run dev
```

Open http://localhost:5173

## What's seeded

| Scenario | Trigger | Bot action |
|----------|---------|------------|
| **Double-booking** | Client sync overlaps Architecture review (tomorrow 10 AM) | Detects conflict → proposes reschedule → **auto-executes** |
| **Missed deadline** | Expense report (2 days overdue), Security audit (6h overdue) | Drafts apology + extension emails |
| **Approaching deadline** | Q2 deck (20h), Checkout bug (8h) | Drafts proactive extension requests |
| **Meeting prep** | Q2 Board Review (in ~3h, has prior notes) | Surfaces notes + LLM prep checklist |
| **Background** | ~30 days of tasks, events, habits | Powers Tasks & Calendar views |

## Live demo flow (3 min)

1. **Open Dashboard** — read the tagline aloud.
2. **Click "Save My Day"** — bot runs autonomously (no user prompts).
3. **Walk through the timeline:**
   - "It caught a double-booking before your morning started."
   - "It didn't just alert you — it rescheduled the conflict."
   - "Two deadlines were missed — it drafted recovery emails."
   - "Two more are due soon — extension emails ready to send."
   - "Board review in 3 hours — here's your prep from last meeting's notes."
4. **Scroll to Agent Activity** — every action logged with confidence scores.
5. **Optional:** Open **Chat** and ask *"What should I prioritize today?"*

## API equivalent (for judges)

```bash
curl -X POST http://localhost:8000/v1/agent/run
```

Returns `tagline`, `narrative[]`, `deadline_rescue[]`, `meeting_prep[]`, `summary`.

## Guardrails to mention

- **LangGraph** state machine — explicit, auditable agent workflow
- **LangChain** LLM with confidence scoring

- LLM confidence scoring (low confidence = verify before acting)
- Input sanitization on all user-facing endpoints
- Rate limiting on task creation
- Graceful offline fallback (works without API key)
- All actions audit-logged in `agent_logs`
- Synthetic sandbox — no real PII

## Closing line

*"Reminders tell you what's wrong. Last Minute Life Saver fixes it — reschedules your calendar, drafts your emails, and preps your meetings. Autonomously."*
