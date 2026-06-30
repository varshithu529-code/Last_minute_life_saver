"""Build proactive chat replies and action card payloads from agent results."""

from app.services.agent.graph import PITCH_TAGLINE


def build_action_cards(result: dict) -> list[dict]:
    """Map LangGraph workflow result to wireframe action cards."""
    cards = []

    for conflict in result.get("conflicts") or []:
        proposal = (result.get("reschedule_proposals") or [{}])[0]
        executed = result.get("reschedule_executed")
        cards.append(
            {
                "type": "conflict",
                "id": f"conflict-{conflict['event_b']['id']}",
                "title": "Meeting Conflict Detected",
                "subtitle": f"{conflict['event_a']['title']} ↔ {conflict['event_b']['title']}",
                "action": proposal.get("proposal", "Reschedule proposed"),
                "status": "executed" if executed else "proposed",
                "event_id": conflict["event_b"]["id"],
                "proposal": proposal,
            }
        )

    for rescue in result.get("deadline_rescue") or []:
        cards.append(
            {
                "type": "deadline",
                "id": f"deadline-{rescue['task_id']}",
                "title": rescue["title"],
                "subtitle": "Missed deadline" if rescue["rescue_type"] == "missed_deadline" else "Due soon",
                "action": "Drafted extension email",
                "draft_email": rescue.get("draft_email", ""),
                "confidence": rescue.get("confidence", 0.5),
                "rescue_type": rescue["rescue_type"],
            }
        )

    for prep in result.get("meeting_prep") or []:
        cards.append(
            {
                "type": "prep",
                "id": f"prep-{prep['event_id']}",
                "title": "Meeting Prep",
                "subtitle": prep.get("title", "Upcoming meeting"),
                "action": "Last meeting notes + prep checklist ready",
                "previous_notes": prep.get("previous_notes"),
                "prep_checklist": prep.get("prep_checklist", ""),
                "confidence": prep.get("confidence", 0.5),
            }
        )

    return cards


def build_proactive_reply(message: str, cards: list[dict], llm_reply: str) -> str:
    """Prefer a concise proactive reply when actions were taken."""
    lower = message.lower()

    if not cards:
        return llm_reply

    if any(c["type"] == "deadline" for c in cards):
        card = next(c for c in cards if c["type"] == "deadline")
        urgency = "overdue" if card.get("rescue_type") == "missed_deadline" else "due soon"
        return (
            f"I noticed {card['title']} is {urgency}. "
            f"I've drafted an extension email to your manager — want me to send it?"
        )

    if any(c["type"] == "conflict" for c in cards):
        card = next(c for c in cards if c["type"] == "conflict")
        if card.get("status") == "executed":
            return (
                f"I found a scheduling conflict between your meetings. "
                f"{card['action']} — want me to keep this change or undo it?"
            )
        return (
            f"You're double-booked: {card['subtitle']}. "
            f"I can {card['action'].lower()} — confirm?"
        )

    if any(c["type"] == "prep" for c in cards):
        card = next(c for c in cards if c["type"] == "prep")
        return (
            f"Your {card['subtitle']} is coming up. "
            f"I've pulled last meeting notes and a prep checklist — open them below?"
        )

    if "save" in lower or "rescue" in lower:
        return f"{PITCH_TAGLINE} Here's everything I handled for you today."

    return llm_reply
