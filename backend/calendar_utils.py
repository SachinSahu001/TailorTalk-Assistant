import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from dateutil.parser import isoparse
import pytz 
from google.oauth2 import service_account 
from googleapiclient.discovery import build

load_dotenv()

# 🔐 Environment variables
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CALENDAR_SERVICE_ACCOUNT")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

SCOPES = ['https://www.googleapis.com/auth/calendar']
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build('calendar', 'v3', credentials=credentials)

def get_free_slots(start_time, end_time, duration_minutes=30):
    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start_time.isoformat(),
        timeMax=end_time.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    free_slots = []
    current = start_time

    for event in events:
        event_start = isoparse(event['start']['dateTime'])
        if current + timedelta(minutes=duration_minutes) <= event_start:
            free_slots.append((current, event_start))
        current = isoparse(event['end']['dateTime'])

    if current + timedelta(minutes=duration_minutes) <= end_time:
        free_slots.append((current, end_time))

    return free_slots

def create_event(start_time, end_time, summary="Meeting with TailorTalk Bot"):
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
    return service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
