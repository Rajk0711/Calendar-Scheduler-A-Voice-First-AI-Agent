import os
import json
import datetime
from typing import Optional, List, Dict
from langchain_core.tools import tool
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Directory for logs (sharing with Version 1.0 for consistency if needed, but keeping it local to Version 2 if desired)
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "event_logs")
os.makedirs(LOG_DIR, exist_ok=True)

def get_calendar_service():
    """Builds the Google Calendar service using OAuth 2.0 Credentials."""
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        print("Error: Missing Google OAuth 2.0 credentials in environment variables.")
        return None

    try:
        creds = Credentials(
            None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=['https://www.googleapis.com/auth/calendar']
        )

        # Refresh the access token if it's invalid or expired
        if not creds.valid:
            creds.refresh(Request())

        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Error creating Google Calendar service: {e}")
        return None

def log_action(action: str, details: str, target_date: Optional[str] = None):
    """Log calendar actions to a daily file."""
    log_date = target_date if target_date else datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"event_log_{log_date}.txt")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {action.upper()}: {details}\n"
    
    with open(log_file, "a") as f:
        f.write(log_entry)

@tool
def list_calendars() -> List[Dict]:
    """Lists all calendars available in the user's account."""
    service = get_calendar_service()
    if not service:
        return [{"error": "Authentication failed"}]
    
    try:
        calendar_list = service.calendarList().list().execute()
        return calendar_list.get('items', [])
    except Exception as e:
        return [{"error": str(e)}]

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
        return [{"error": "Authentication failed"}]

    try:
        events_result = service.events().list(
            calendarId='primary', 
            timeMin=time_min, 
            timeMax=time_max,
            singleEvents=True, 
            orderBy='startTime'
        ).execute()
        return events_result.get('items', [])
    except Exception as e:
        return [{"error": str(e)}]

@tool
def get_event_details(event_id: str) -> Dict:
    """Retrieves full details of a specific event by its ID."""
    service = get_calendar_service()
    if not service:
        return {"error": "Authentication failed"}
    
    try:
        return service.events().get(calendarId='primary', eventId=event_id).execute()
    except Exception as e:
        return {"error": str(e)}

@tool
def create_event(summary: str, start_time: str, end_time: str, description: Optional[str] = None) -> Dict:
    """
    Schedule a new event on the calendar.
    Args:
        summary: Title of the meeting
        start_time: Start time in ISO format
        end_time: End time in ISO format
        description: Optional description of the event
    """
    target_date = start_time.split("T")[0]
    log_action("create", f"Summary: {summary}, Start: {start_time}, End: {end_time}", target_date=target_date)
    
    service = get_calendar_service()
    if not service:
        return {"error": "Authentication failed"}

    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_time},
        'end': {'dateTime': end_time},
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        return event
    except Exception as e:
        return {"error": str(e)}

@tool
def update_event(event_id: str, summary: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None) -> Dict:
    """
    Update an existing event.
    Args:
        event_id: The ID of the event to update
        summary: New title
        start_time: New start time
        end_time: New end time
    """
    service = get_calendar_service()
    if not service:
        return {"error": "Authentication failed"}
    
    try:
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        if summary: event['summary'] = summary
        if start_time: event['start'] = {'dateTime': start_time}
        if end_time: event['end'] = {'dateTime': end_time}
        
        updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
        
        # Log update
        start = updated_event.get('start', {}).get('dateTime') or updated_event.get('start', {}).get('date')
        target_date = start.split("T")[0] if start else None
        log_action("update", f"ID: {event_id}, Summary: {summary}", target_date=target_date)
        
        return updated_event
    except Exception as e:
        return {"error": str(e)}

@tool
def delete_event(event_id: str) -> str:
    """Deletes an event from the calendar."""
    service = get_calendar_service()
    if not service:
        return "Authentication failed"
    
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        log_action("delete", f"ID: {event_id}")
        return f"Event {event_id} deleted successfully."
    except Exception as e:
        return f"Error deleting event: {str(e)}"

@tool
def check_availability(start_time: str, end_time: str) -> bool:
    """
    Check if a specific time slot is free (no overlaps).
    Args:
        start_time: Start time in ISO format
        end_time: End time in ISO format
    """
    events = list_events.invoke({"time_min": start_time, "time_max": end_time})
    if isinstance(events, list) and len(events) > 0:
        if "error" in events[0]:
            return False
        return False # Overlap found
    return True # Free

@tool
def find_available_slots(date_str: str, start_hour: int = 9, end_hour: int = 18) -> List[Dict]:
    """
    Finds free time slots on a given date during working hours.
    Args:
        date_str: Date in YYYY-MM-DD format
        start_hour: Start of the working day (e.g., 9 for 9 AM)
        end_hour: End of the working day (e.g., 18 for 6 PM)
    """
    time_min = f"{date_str}T{start_hour:02d}:00:00+05:30"
    time_max = f"{date_str}T{end_hour:02d}:00:00+05:30"
    
    events = list_events.invoke({"time_min": time_min, "time_max": time_max})
    if isinstance(events, dict) and "error" in events:
        return []

    # Sort events by start time
    sorted_events = sorted(events, key=lambda x: x['start'].get('dateTime', x['start'].get('date')))
    
    available_slots = []
    current_time = datetime.datetime.fromisoformat(time_min.replace("Z", "+00:00"))
    end_time = datetime.datetime.fromisoformat(time_max.replace("Z", "+00:00"))

    for event in sorted_events:
        event_start = datetime.datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')).replace("Z", "+00:00"))
        event_end = datetime.datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')).replace("Z", "+00:00"))
        
        if event_start > current_time:
            available_slots.append({
                "start": current_time.isoformat(),
                "end": event_start.isoformat()
            })
        
        if event_end > current_time:
            current_time = event_end

    if current_time < end_time:
        available_slots.append({
            "start": current_time.isoformat(),
            "end": end_time.isoformat()
        })

    return available_slots

@tool
def send_email_notification(recipient_email: str, subject: str, body: str) -> str:
    """Send an email notification via Gmail SMTP."""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    email_address = os.environ.get("EMAIL_ADDRESS")
    email_password = os.environ.get("EMAIL_PASSWORD")

    if not email_address or not email_password:
        return "Error: Email credentials not configured."

    try:
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)
        
        return f"Email sent successfully to {recipient_email}"
    except Exception as e:
        return f"Error sending email: {str(e)}"
