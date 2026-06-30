"""Calendar provider abstractions — Outlook (Graph) and Google Calendar."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)


class CalendarEvent:
    """Provider-agnostic calendar event."""

    def __init__(
        self,
        title: str,
        start: datetime,
        end: datetime,
        external_id: str | None = None,
        location: str | None = None,
        attendees: list[str] | None = None,
    ) -> None:
        self.title = title
        self.start = start
        self.end = end
        self.external_id = external_id
        self.location = location
        self.attendees = attendees or []


class CalendarProvider(ABC):
    """Abstract calendar integration."""

    @abstractmethod
    def list_events(
        self, start: datetime, end: datetime
    ) -> list[CalendarEvent]:
        pass

    @abstractmethod
    def create_event(self, event: CalendarEvent) -> CalendarEvent:
        pass

    @abstractmethod
    def update_event(self, event_id: str, event: CalendarEvent) -> CalendarEvent:
        pass

    @abstractmethod
    def delete_event(self, event_id: str) -> bool:
        pass


class OutlookCalendarProvider(CalendarProvider):
    """Microsoft Graph API integration (stub for OAuth2 flow)."""

    def __init__(self) -> None:
        settings = get_settings()
        self.client_id = settings.ms_client_id
        self.calendar_id = settings.calendar_id
        self._token: str | None = None

    def _authenticated(self) -> bool:
        return bool(self.client_id and self._token)

    def list_events(
        self, start: datetime, end: datetime
    ) -> list[CalendarEvent]:
        if not self._authenticated():
            logger.info("Outlook not authenticated — returning empty list")
            return []
        # Production: GET /me/calendarView?startDateTime=&endDateTime=
        return []

    def create_event(self, event: CalendarEvent) -> CalendarEvent:
        logger.info("Outlook create_event stub: %s", event.title)
        event.external_id = event.external_id or f"outlook-{event.start.isoformat()}"
        return event

    def update_event(self, event_id: str, event: CalendarEvent) -> CalendarEvent:
        logger.info("Outlook update_event stub: %s", event_id)
        event.external_id = event_id
        return event

    def delete_event(self, event_id: str) -> bool:
        logger.info("Outlook delete_event stub: %s", event_id)
        return True


class GoogleCalendarProvider(CalendarProvider):
    """Google Calendar API integration (stub for OAuth2 flow)."""

    def __init__(self) -> None:
        settings = get_settings()
        self.client_id = settings.google_client_id
        self.calendar_id = settings.calendar_id
        self._credentials: Any = None

    def _authenticated(self) -> bool:
        return bool(self.client_id and self._credentials)

    def list_events(
        self, start: datetime, end: datetime
    ) -> list[CalendarEvent]:
        if not self._authenticated():
            logger.info("Google Calendar not authenticated — returning empty list")
            return []
        return []

    def create_event(self, event: CalendarEvent) -> CalendarEvent:
        logger.info("Google create_event stub: %s", event.title)
        event.external_id = event.external_id or f"gcal-{event.start.isoformat()}"
        return event

    def update_event(self, event_id: str, event: CalendarEvent) -> CalendarEvent:
        logger.info("Google update_event stub: %s", event_id)
        event.external_id = event_id
        return event

    def delete_event(self, event_id: str) -> bool:
        logger.info("Google delete_event stub: %s", event_id)
        return True


def get_calendar_provider() -> CalendarProvider:
    """Factory for configured calendar provider."""
    settings = get_settings()
    if settings.calendar_provider == "google_calendar":
        return GoogleCalendarProvider()
    return OutlookCalendarProvider()
