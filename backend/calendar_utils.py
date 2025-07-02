import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from dateutil.parser import isoparse
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ✅ Load environment variables
load_dotenv()

# 🔐 Required environment values
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CALENDAR_SERVICE_ACCOUNT")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

if not SERVICE_ACCOUNT_FILE or not CALENDAR_ID:
    raise ValueError("Missing required env vars: GOOGLE_CALENDAR_SERVICE_ACCOUNT or GOOGLE_CALENDAR_ID")

# 🔑 Authenticate service account
SCOPES = ['https://www.googleapis.com/auth/calendar']
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build('calendar', 'v3', credentials=credentials)

# ✅ Get free slots between two times
def get_free_slots(start_time: datetime, end_time: datetime, duration_minutes=30):
    print(f"🔍 Checking availability from {start_time} to {end_time}...")

    # Convert to timezone-aware ISO format
    tz = pytz.timezone(TIMEZONE)
    start_time = tz.localize(start_time) if start_time.tzinfo is None else start_time
    end_time = tz.localize(end_time) if end_time.tzinfo is None else end_time

    try:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_time.isoformat(),
            timeMax=end_time.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
    except HttpError as e:
        print(f"❌ Error fetching events: {e}")
        return []

    free_slots = []
    current = start_time

    for event in events:
        event_start = isoparse(event['start'].get('dateTime', event['start'].get('date')))
        event_end = isoparse(event['end'].get('dateTime', event['end'].get('date')))

        if current + timedelta(minutes=duration_minutes) <= event_start:
            free_slots.append((current, event_start))
        current = max(current, event_end)

    if current + timedelta(minutes=duration_minutes) <= end_time:
        free_slots.append((current, end_time))

    return free_slots

# ✅ Create new event
def create_event(start_time: datetime, end_time: datetime, summary="Meeting with TailorTalk Bot"):
    tz = pytz.timezone(TIMEZONE)
    start_time = tz.localize(start_time) if start_time.tzinfo is None else start_time
    end_time = tz.localize(end_time) if end_time.tzinfo is None else end_time

    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': TIMEZONE,
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': TIMEZONE,
        },
    }

    print(f"📅 Creating event: {event}")

    try:
        calendar_id = os.getenv("CALENDAR_ID", "primary")
        created_event = service.events().insert(calendarId="ef3ad66c534b452a1e081e4eb72a83d5ed070e14fefbc0cab68982197daca075@group.calendar.google.com", body=event).execute()
        print(f"✅ Event created: {created_event.get('htmlLink')}")
        return created_event
    except HttpError as e:
        print(f"❌ Failed to create event: {e}")
        raise RuntimeError(f"Failed to book meeting: {e}")
