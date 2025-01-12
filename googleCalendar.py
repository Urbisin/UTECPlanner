import datetime
import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta

SCOPES = ["https://www.googleapis.com/auth/calendar"]

DAYS_MAPPING = {
    "Lunes": 0,  # Monday
    "Martes": 1,  # Tuesday
    "Miércoles": 2,  # Wednesday
    "Jueves": 3,  # Thursday
    "Viernes": 4,  # Friday
    "Sábado": 5,  # Saturday
    "Domingo": 6  # Sunday
}

def get_next_weekday(start_date, weekday):
    days_ahead = weekday - start_date.weekday()
    if days_ahead < 0:
        days_ahead += 7
    return start_date + timedelta(days=days_ahead)

def get_initial_date():
    with open('config.json', 'r') as file:
        config = json.load(file)
    return config['initial_date']

def create_events_from_schedule(initial_date):
    events = []

    initial_date = datetime.strptime(initial_date, "%Y-%m-%d")

    with open("courses.json", "r") as courses:
        courses = json.load(courses)
        for course in courses:
            for schedule in course["schedule"]:
                day_name = schedule["day"]
                hour_range = schedule["hour"]
                class_type = schedule["type"]
                classroom = schedule["classroom"]

                weekday_number = DAYS_MAPPING[day_name]

                event_date = get_next_weekday(initial_date, weekday_number)

                start_hour, end_hour = hour_range.split("-")

                start_time = datetime.combine(event_date, datetime.strptime(start_hour, "%H:%M").time())
                end_time = datetime.combine(event_date, datetime.strptime(end_hour, "%H:%M").time())

                event = {
                    'summary': f'{course["name"]} - {classroom}',
                    'location': 'Universidad de Ingeniería y Tecnología - UTEC, Jr. Medrano Silva 165, Barranco 15063, Perú',
                    'description': f'{class_type} {course["section"]}',
                    'start': {
                        'dateTime': start_time.isoformat(),
                        'timeZone': 'America/Lima',
                    },
                    'end': {
                        'dateTime': end_time.isoformat(),
                        'timeZone': 'America/Lima',
                    },
                    'recurrence': [
                        'RRULE:FREQ=WEEKLY;COUNT=8'
                    ]
                }
                events.append(event)

    return events

def create_schedule_calendar():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10  events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        initial_date = get_initial_date()
        event = create_events_from_schedule(initial_date)
        for e in event:
            service.events().insert(calendarId="primary", body=e).execute()

    except HttpError as error:
        print(f"An error occurred: {error}")
