import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes needed for the Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    """
    Helper script to get a refresh token for Google Calendar API.
    1. Go to Google Cloud Console -> APIs & Services -> Credentials.
    2. Create 'OAuth 2.0 Client ID' of type 'Desktop app'.
    3. Name it "Calendar Agent Desktop".
    4. Download the JSON file and rename it to 'client_secrets.json' in this folder.
    5. Run this script.
    """
    client_secrets_path = 'client_secrets.json'
    
    if not os.path.exists(client_secrets_path):
        print(f"Error: {client_secrets_path} not found.")
        print("Please download your OAuth client secret JSON from Google Cloud Console and rename it to 'client_secrets.json'.")
        return

    try:
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
        # For Desktop apps, we don't need to specify a port, it uses a dynamic loopback
        creds = flow.run_local_server(prompt='consent', access_type='offline')
        
        print("\n--- AUTHENTICATION SUCCESSFUL ---")
        print(f"GOOGLE_CLIENT_ID={creds.client_id}")
        print(f"GOOGLE_CLIENT_SECRET={creds.client_secret}")
        print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
        print("----------------------------------")
        print("\nCopy these values into your .env file.")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
