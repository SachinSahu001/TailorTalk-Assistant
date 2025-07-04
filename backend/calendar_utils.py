import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ✅ Load environment variables from .env
load_dotenv()

# ✅ Load service account JSON from environment variable
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")
if not GOOGLE_CREDENTIALS:
    raise EnvironmentError("❌ GOOGLE_CREDENTIALS not set in environment.")

SCOPES = ['https://www.googleapis.com/auth/calendar']

# ✅ Parse credentials JSON string
credentials = service_account.Credentials.from_service_account_info(
    json.loads(GOOGLE_CREDENTIALS), scopes=SCOPES
)

# ✅ Setup Google Calendar service
service = build("calendar", "v3", credentials=credentials)

# ✅ Calendar ID and Timezone
calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")


def get_free_slots(start: datetime, end: datetime):
    """Returns a list of available 30-minute time slots."""
    try:
        body = {
            "timeMin": start.isoformat(),
            "timeMax": end.isoformat(),
            "timeZone": TIMEZONE,
            "items": [{"id": calendar_id}]
        }

        response = service.freebusy().query(body=body).execute()
        busy_times = response["calendars"][calendar_id]["busy"]

        free_slots = []
        current_time = start

        while current_time + timedelta(minutes=30) <= end:
            next_time = current_time + timedelta(minutes=30)
            conflict = any(
                current_time < datetime.fromisoformat(slot["end"]) and
                next_time > datetime.fromisoformat(slot["start"])
                for slot in busy_times
            )
            if not conflict:
                free_slots.append((current_time, next_time))
            current_time = next_time

        return free_slots

    except HttpError as error:
        print(f"❌ Error fetching free slots: {error}")
        return []


def create_event(start: datetime, end: datetime):
    """Creates a 30-minute Google Calendar event."""
    try:
        event = {
            "summary": "Meeting with TailorTalk Bot",
            "start": {
                "dateTime": start.isoformat(),
                "timeZone": TIMEZONE
            },
            "end": {
                "dateTime": end.isoformat(),
                "timeZone": TIMEZONE
            }
        }

        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"✅ Event created: {created_event.get('htmlLink')}")
        return created_event

    except HttpError as e:
        print(f"❌ Failed to create event: {e}")
        raise RuntimeError(f"Failed to book meeting: {e}")
