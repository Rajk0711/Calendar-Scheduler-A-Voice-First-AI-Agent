import os
import json
import datetime
from typing import Optional, List, Dict
from langchain_core.tools import tool
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Mock Data
MOCK_EVENTS = [
    {
        "summary": "Team Meeting",
        "start": {"dateTime": (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0).isoformat()},
        "end": {"dateTime": (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=11, minute=0, second=0, microsecond=0).isoformat()},
    },
    {
        "summary": "Team Outing",
        "start": {"dateTime": (datetime.datetime.now() + datetime.timedelta(days=4)).replace(hour=14, minute=0, second=0, microsecond=0).isoformat()},
        "end": {"dateTime": (datetime.datetime.now() + datetime.timedelta(days=4)).replace(hour=17, minute=0, second=0, microsecond=0).isoformat()},
    },
    {
        "summary": "Client Meeting",
        "start": {"dateTime": (datetime.datetime.now() + datetime.timedelta(days=7)).replace(hour=11, minute=0, second=0, microsecond=0).isoformat()},
        "end": {"dateTime": (datetime.datetime.now() + datetime.timedelta(days=7)).replace(hour=12, minute=0, second=0, microsecond=0).isoformat()},
    },
    {
        "summary": "Day Off",
        "start": {"dateTime": (datetime.datetime.now() + datetime.timedelta(days=9)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()},
        "end": {"dateTime": (datetime.datetime.now() + datetime.timedelta(days=9)).replace(hour=23, minute=59, second=59, microsecond=0).isoformat()},
    },
    {
        "summary": "Project Review",
        "start": {"dateTime": (datetime.datetime.now() + datetime.timedelta(days=10)).replace(hour=15, minute=0, second=0, microsecond=0).isoformat()},
        "end": {"dateTime": (datetime.datetime.now() + datetime.timedelta(days=10)).replace(hour=16, minute=0, second=0, microsecond=0).isoformat()},
    },
    {
        "summary": "Dentist Appointment",
        "start": {"dateTime": (datetime.datetime.now() + datetime.timedelta(days=11)).replace(hour=9, minute=0, second=0, microsecond=0).isoformat()},
        "end": {"dateTime": (datetime.datetime.now() + datetime.timedelta(days=11)).replace(hour=10, minute=0, second=0, microsecond=0).isoformat()},
    }
]

def get_calendar_service():
    # Try Streamlit Secrets first (Cloud)
    try:
        import streamlit as st
        if "GOOGLE_CREDENTIALS" in st.secrets:
            service_account_info = st.secrets["GOOGLE_CREDENTIALS"]
    except ImportError:
        pass

    # Fallback to Environment Variable (Local)
    if not service_account_info:
        service_account_info = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")

    if not service_account_info:
        return None
    
    try:
        # Check if info is dict (from secrets) or string (from env)
        if isinstance(service_account_info, str):
            creds_dict = json.loads(service_account_info)
        else:
            creds_dict = service_account_info
            
        creds = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=['https://www.googleapis.com/auth/calendar']
        )
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Error creating service: {e}")
        return None

@tool
def list_events(time_min: str, time_max: str) -> List[Dict]:
    """
    List calendar events for a given date range.
    Args:
        time_min: Start time in ISO format (e.g., 2023-10-25T10:00:00Z)
        time_max: End time in ISO format
    """
    service = get_calendar_service()
    
    if not service:
        print(f"[MOCK] Listing events from {time_min} to {time_max}")
        # Simple mock filter
        return MOCK_EVENTS

    try:
        events_result = service.events().list(
            calendarId='primary', timeMin=time_min, timeMax=time_max,
            singleEvents=True, orderBy='startTime'
        ).execute()
        return events_result.get('items', [])
    except Exception as e:
        return [{"error": str(e)}]

@tool
def create_event(summary: str, start_time: str, end_time: str) -> Dict:
    """
    Schedule a new event on the calendar.
    Args:
        summary: Title of the meeting
        start_time: Start time in ISO format
        end_time: End time in ISO format
    """
    service = get_calendar_service()
    
    if not service:
        print(f"[MOCK] Creating event: {summary}")
        new_event = {
            "summary": summary,
            "start": {"dateTime": start_time},
            "end": {"dateTime": end_time}
        }
        MOCK_EVENTS.append(new_event)
        return new_event

    event = {
        'summary': summary,
        'start': {'dateTime': start_time},
        'end': {'dateTime': end_time},
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        return event
    except Exception as e:
        return {"error": str(e)}

@tool
def check_availability(start_time: str, end_time: str) -> bool:
    """
    Check if a specific time slot is free.
    Args:
        start_time: Start time in ISO format
        end_time: End time in ISO format
    """
    events = list_events.invoke({"time_min": start_time, "time_max": end_time})
    
    # If events is a list of dicts, check if any overlap
    # Simplified check: if list is not empty, assume busy (unless it's an error)
    if isinstance(events, list) and len(events) > 0:
        if "error" in events[0]:
            return False # Assume busy on error? Or handle differently.
        return False # Busy
    
    return True # Free

@tool
def send_email_notification(recipient_email: str, subject: str, body: str) -> str:
    """
    Send an email notification via Gmail SMTP.
    Requires EMAIL_ADDRESS and EMAIL_PASSWORD in secrets or environment.
    Args:
        recipient_email: The email address to send to.
        subject: The subject of the email.
        body: The plain text body of the email.
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    email_address = os.environ.get("EMAIL_ADDRESS")
    email_password = os.environ.get("EMAIL_PASSWORD")

    # Try Streamlit Secrets if env vars are missing
    try:
        import streamlit as st
        if not email_address and "EMAIL_ADDRESS" in st.secrets:
            email_address = st.secrets["EMAIL_ADDRESS"]
        if not email_password and "EMAIL_PASSWORD" in st.secrets:
            email_password = st.secrets["EMAIL_PASSWORD"]
    except ImportError:
        pass

    if not email_address or not email_password:
        return "Error: Email credentials not configured."

    try:
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to Gmail SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)
        
        return f"Email sent successfully to {recipient_email}"
    except Exception as e:
        return f"Error sending email: {str(e)}"
