"""
calendar_tool.py
Calendar agent - read upcoming events and create new ones using your own
Google account. Free, uses the same OAuth pattern as the email agent.
"""

import os
import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "calendar_token.json"  # separate token file from email's


def get_calendar_service():
    """Authenticate and return a Google Calendar API service object."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


# ---------- CALENDAR READ AGENT ----------
def get_upcoming_events(max_results: int = 5) -> str:
    """List the user's upcoming calendar events."""
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + "Z"

        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        events = events_result.get("items", [])

        if not events:
            return "No upcoming events found."

        summaries = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summaries.append(f"- {event.get('summary', '(no title)')} at {start}")

        return "Upcoming events:\n" + "\n".join(summaries)
    except Exception as e:
        return f"Calendar read agent error: {e}"


# ---------- CALENDAR CREATE AGENT ----------
def create_event(title: str, start_datetime: str, end_datetime: str, description: str = "") -> str:
    """Create a new calendar event.
    start_datetime and end_datetime must be ISO format, e.g. '2026-06-25T15:00:00'
    """
    try:
        service = get_calendar_service()

        event = {
            "summary": title,
            "description": description,
            "start": {"dateTime": start_datetime, "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end_datetime, "timeZone": "Asia/Kolkata"},
        }

        created = service.events().insert(calendarId="primary", body=event).execute()
        return f"Event created: {created.get('summary')} at {created.get('start').get('dateTime')} (link: {created.get('htmlLink')})"
    except Exception as e:
        return f"Calendar create agent error: {e}"