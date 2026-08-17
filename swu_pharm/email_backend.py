import base64
import json

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class GmailAPIBackend(BaseEmailBackend):
    def open(self):
        if hasattr(self, 'service'):
            return False

        key_json = base64.b64decode(settings.GMAIL_SERVICE_ACCOUNT_KEY_B64).decode()
        key_info = json.loads(key_json)

        credentials = service_account.Credentials.from_service_account_info(
            key_info,
            scopes=SCOPES,
            subject=settings.GMAIL_SENDER,
        )

        self.service = build('gmail', 'v1', credentials=credentials)
        return True

    def close(self):
        self.service = None

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        new_conn_created = self.open()
        if not hasattr(self, 'service'):
            return 0

        num_sent = 0
        for message in email_messages:
            try:
                mime_message = message.message()
                raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
                self.service.users().messages().send(
                    userId='me',
                    body={'raw': raw_message},
                ).execute()
                num_sent += 1
            except Exception:
                if not self.fail_silently:
                    raise

        if new_conn_created:
            self.close()

        return num_sent