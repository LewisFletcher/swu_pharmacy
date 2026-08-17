import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def send_gmail(to, subject, body, html_body=None, sender=None):
    sender = sender or settings.GMAIL_SENDER

    key_json = base64.b64decode(settings.GMAIL_SERVICE_ACCOUNT_KEY_B64).decode()
    key_info = json.loads(key_json)

    credentials = service_account.Credentials.from_service_account_info(
        key_info,
        scopes=SCOPES,
        subject=sender,
    )

    service = build('gmail', 'v1', credentials=credentials)

    if html_body:
        message = MIMEMultipart('alternative')
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        message.attach(MIMEText(html_body, 'html'))
    else:
        message = MIMEText(body)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    sent = service.users().messages().send(
        userId='me',
        body={'raw': raw_message},
    ).execute()

    return sent