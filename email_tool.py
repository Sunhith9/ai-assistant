"""
email_tool.py
Gmail agent - read and send emails using your own Google account.
Free, uses OAuth - only YOU can authorize access to YOUR inbox.
"""

import os
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def get_gmail_service():
    """Authenticate and return a Gmail API service object."""
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

    return build("gmail", "v1", credentials=creds)


# ---------- EMAIL READ AGENT ----------
def read_recent_emails(max_results: int = 5) -> str:
    """Read subject + sender of the most recent emails in your inbox."""
    try:
        service = get_gmail_service()
        results = service.users().messages().list(
            userId="me", maxResults=max_results, labelIds=["INBOX"]
        ).execute()
        messages = results.get("messages", [])

        if not messages:
            return "No emails found."

        summaries = []
        for msg in messages:
            msg_data = service.users().messages().get(
                userId="me", id=msg["id"], format="metadata",
                metadataHeaders=["From", "Subject", "Date"]
            ).execute()
            headers = {h["name"]: h["value"] for h in msg_data["payload"]["headers"]}
            snippet = msg_data.get("snippet", "")
            summaries.append(
                f"From: {headers.get('From', 'Unknown')}\n"
                f"Subject: {headers.get('Subject', '(no subject)')}\n"
                f"Date: {headers.get('Date', '')}\n"
                f"Preview: {snippet}\n"
            )

        return "\n---\n".join(summaries)
    except Exception as e:
        return f"Email read agent error: {e}"


# ---------- CONTACT LOOKUP AGENT ----------
def find_email_by_name(name: str) -> str:
    """Search past emails (sent + received) to find an email address matching a name."""
    try:
        service = get_gmail_service()
        query = f'"{name}"'
        results = service.users().messages().list(
            userId="me", q=query, maxResults=10
        ).execute()
        messages = results.get("messages", [])

        if not messages:
            return f"No emails found matching '{name}'. Please provide the exact email address."

        found = set()
        for msg in messages:
            msg_data = service.users().messages().get(
                userId="me", id=msg["id"], format="metadata",
                metadataHeaders=["From", "To"]
            ).execute()
            headers = {h["name"]: h["value"] for h in msg_data["payload"]["headers"]}
            for field in ("From", "To"):
                value = headers.get(field, "")
                if name.lower() in value.lower():
                    found.add(value)

        if not found:
            return f"No exact match found for '{name}'. Please provide the exact email address."

        return "Possible matches found:\n" + "\n".join(f"- {f}" for f in found)
    except Exception as e:
        return f"Contact lookup agent error: {e}"


# ---------- EMAIL DRAFT AGENT (preview before sending) ----------
def draft_email(to: str, subject: str, body: str) -> str:
    """Show a preview of an email before sending. Always call this BEFORE send_email
    so the user can review and approve the content first."""
    return (
        f"DRAFT EMAIL (not sent yet):\n"
        f"To: {to}\n"
        f"Subject: {subject}\n"
        f"Body:\n{body}\n\n"
        f"Ask the user to confirm before calling send_email."
    )


# ---------- EMAIL SEND AGENT ----------
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email from your Gmail account. Only call this after the
    user has explicitly confirmed the draft shown by draft_email."""
    try:
        service = get_gmail_service()

        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        sent = service.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()

        return f"Email sent to {to} (id: {sent['id']})"
    except Exception as e:
        return f"Email send agent error: {e}"