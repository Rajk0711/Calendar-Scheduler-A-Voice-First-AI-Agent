# GCP & Google Calendar API Setup Guide

This guide will walk you through creating a free Google Cloud Platform (GCP) account and setting up the Google Calendar API for your AI Scheduler.

## Phase 1: Create a Free GCP Account

1.  **Go to the Google Cloud Console**:
    - Visit [console.cloud.google.com](https://console.cloud.google.com/).
2.  **Sign In**:
    - Use your Google (Gmail) account.
3.  **Activate Free Trial**:
    - You should see a banner asking you to activate your free trial (usually $300 credit for 90 days).
    - Click **"Activate"** or **"Try for Free"**.
    - You will need to provide a credit/debit card for identity verification. *Note: You won't be charged unless you manually upgrade after the trial ends.*

## Phase 2: Create a Project

1.  Click the project dropdown in the top bar (it might say "My First Project" or "Select a project").
2.  Click **"New Project"**.
3.  **Project Name**: Enter something like `AI-Scheduler`.
4.  Click **"Create"**.
5.  Wait a moment, then select your new project from the notification bell or the dropdown.

## Phase 3: Enable Google Calendar API

1.  In the left sidebar, go to **"APIs & Services"** > **"Library"**.
2.  In the search bar, type `Google Calendar API`.
3.  Click on **"Google Calendar API"** from the results.
4.  Click **"Enable"**.

## Phase 4: Configure OAuth Consent Screen

1.  Go to **"APIs & Services"** > **"OAuth consent screen"**.
2.  **User Type**: Select **"External"** (since you are testing personally, but this is standard for most apps) or **"Internal"** if you have a Google Workspace organization. *If you don't have an org, select External.*
3.  Click **"Create"**.
4.  **App Information**:
    - **App name**: `AI Scheduler Agent`
    - **User support email**: Select your email.
    - **Developer contact information**: Enter your email.
5.  Click **"Save and Continue"**.
6.  **Scopes**:
    - Click **"Add or Remove Scopes"**.
    - Search for `calendar` and select `./auth/calendar` (See, edit, share, and permanently delete all the calendars you can access using Google Calendar).
    - Click **"Update"**, then **"Save and Continue"**.
7.  **Test Users**:
    - Click **"Add Users"**.
    - Enter your own email address. *This is critical for "External" apps in testing mode.*
    - Click **"Save and Continue"**.

## Phase 5: Create Credentials (OAuth Client ID)

1.  Go to **"APIs & Services"** > **"Credentials"**.
2.  Click **"+ Create Credentials"** > **"OAuth client ID"**.
3.  **Application type**: Select **"Desktop app"** (since we are running a local python script/Streamlit app).
4.  **Name**: `Desktop Client 1`.
5.  Click **"Create"**.
6.  **Download JSON**:
    - A popup will appear. Click **"Download JSON"**.
    - Rename this file to `credentials.json`.
    - Move it to your project root folder (where `agent.py` or `tools.py` is).

## Usage in Code

To use these credentials, you typically use the `google-auth-oauthlib` library to authenticate the user (you) via a browser popup the first time you run the script. This generates a `token.json` file for subsequent runs.

*Note: The current codebase uses `google-generativeai` (Gemini) which uses an API Key. For Calendar operations, we need the OAuth flow described above.*
