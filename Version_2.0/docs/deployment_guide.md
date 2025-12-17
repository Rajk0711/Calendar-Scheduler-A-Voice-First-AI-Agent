# Deployment Guide: Vercel & Streamlit Cloud

You mentioned needing to deploy using tools like **Vercel** or **GCP**. Here is how they fit into your project:

## The Challenge
Your project is built with **Streamlit** (`ui/app.py`).
- **Streamlit** requires a server that stays "open" (persistent connection) to listen to user interactions.
- **Vercel** is designed for "Serverless" websites—it spins up for a second to answer a request and then shuts down immediately.

**Creating a persistent Streamlit app on Vercel is difficult and often crashes.**

## Recommended Solution

Use the **Best Tool for the Job** approach:
1.  **Streamlit Community Cloud** for `ui/app.py` (Free, Easy, Made by Streamlit).
2.  (Optional) **Vercel** if you wanted to host just the Python logic as an API (advanced).

---

## Option 1: Deploying to Streamlit Community Cloud (Recommended)
This is likely what your assignment accepts as "Deployed Online" for a Python AI app.

1.  **Push Code to GitHub**:
    - Ensure your project is in a GitHub repository.
    - Make sure you have a `requirements.txt` file in the root (or `Version_2.0` folder).
2.  **Sign Up**:
    - Go to [share.streamlit.io](https://share.streamlit.io/).
    - Sign in with GitHub.
3.  **Deploy**:
    - Click **"New App"**.
    - Select your GitHub Repository.
    - **Main file path**: Enter `Version_2.0/ui/app.py`.
    - Click **"Deploy"**.
4.  **Secrets (API Keys)**:
    - Once deployed, go to the App's **Settings** > **Secrets**.
    - Add your `GEMINI_API_KEY`.
    - **Google Calendar Credentials**:
        - You cannot upload the `credentials.json` file directly. Instead, you copy its content into a secret.
        - Create a secret named `GOOGLE_CREDENTIALS` and paste the entire JSON content from your `credentials.json` file.
        - *Note*: You will need to update your python code to read this secret content instead of looking for a file on disk. We can help you refactor that when you are ready to deploy!

---

## Option 2: Using Vercel (For API Only)
If you *must* use Vercel, you should treat your project as a **Backend API**. You would need to convert your agent into a web server (using FastAPI or Flask) and call it from a frontend.

**Why?** Vercel functions have a 10-second timeout limit on the free tier. Your AI agent might take longer than 10 seconds to think + generate audio, leading to "Timeout" errors.

**If you effectively want to check the box for "Vercel":**
1.  Install Vercel CLI: `npm i -g vercel`
2.  Login: `vercel login`
3.  Create a file `api/index.py` (Vercel looks for code in `api/`):
    ```python
    from http.server import BaseHTTPRequestHandler
    
    class handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type','text/plain')
            self.end_headers()
            self.wfile.write('Hello from NextDimensionAI on Vercel!'.encode('utf-8'))
            return
    ```
4.  Deploy: Run `vercel` in your terminal.
5.  This gives you a live URL. It proves you can submit to Vercel, even if the main Streamlit app lives elsewhere.

## Summary Recommendation
For this assignment, assuming the core deliverable is the **Streamlit Interface**:
1.  **Primary**: Deploy the App on **Streamlit Community Cloud**.
2.  **Secondary (for extra credit)**: Deploy a simple "Health Check" API on Vercel to demonstrate mastery of multiple clouds.
