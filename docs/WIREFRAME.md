# Wireframe Flow

## Screen Layout (Home `/`)

```
┌─────────────────────────────────────────────────────────────┐
│  IMPACT METRICS                                             │
│  Conflicts Resolved │ Deadlines Rescued │ Meetings Prepped  │
│  Focus Score ████████░░ 85/100    🔥 Streak: 5 days rescued │
├─────────────────────────────────────────────────────────────┤
│  CHAT (Entry Point)                                         │
│  [Rescue my deadline] [Prep me for meeting] [Resolve...]    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ User: Rescue my deadline                            │   │
│  │ Bot: I noticed Expense Report is due soon. I've     │   │
│  │      drafted an extension email — want me to send?  │   │
│  └─────────────────────────────────────────────────────┘   │
│  [ Ask anything...                              ] [Send]    │
├─────────────────────────────────────────────────────────────┤
│  DYNAMIC INTERVENTION CARDS                                 │
│  ┌─ Conflict Card ──────────────────────────────────────┐  │
│  │ Meeting Conflict Detected                            │  │
│  │ Rescheduled to tomorrow 10 AM   [Undo] [Confirm]     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌─ Deadline Card ──────────────────────────────────────┐  │
│  │ Expense Report Due Soon                              │  │
│  │ Drafted extension email  [Preview Email] [Send]      │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌─ Prep Card ──────────────────────────────────────────┐  │
│  │ Meeting Prep · Q2 Board Review                       │  │
│  │ Notes + checklist ready              [Open Notes]    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## User Flow

1. **Entry** — User types or taps a quick prompt in chat.
2. **Intent routing** — Backend `handle_intent()` maps to LangGraph tools.
3. **Bot bubble** — Proactive natural-language reply (not generic chat).
4. **Action cards** — Matching interventions appear in the panel below.
5. **Metrics update** — Focus score and streak refresh from agent logs + habits.

## Quick Prompts → Actions

| Prompt | Agent action | Card type |
|--------|--------------|-----------|
| Rescue my deadline | `deadline_rescue()` | Deadline card |
| Prep me for meeting | `meeting_prep()` | Prep card |
| Resolve conflict | detect + reschedule | Conflict card |
| Save my day | Full LangGraph workflow | All cards |

## Card Buttons (Demo)

| Button | Behavior |
|--------|----------|
| Undo / Confirm | Toast confirmation (calendar stub) |
| Preview Email | Expands draft inline |
| Send | Toast "Email queued" |
| Open Notes | Expands prior notes + checklist |
