"""
EMAIL COMMAND CENTER
====================
Gmail API integration for the Empire Super Brain.
Allows reading, searching, and sending emails programmatically.
"""
import os
import base64
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

# These will be populated after OAuth setup
GMAIL_CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), '../gmail_credentials.json')
GMAIL_TOKEN_PATH = os.path.join(os.path.dirname(__file__), '../gmail_token.json')

class EmailCommander:
    def __init__(self):
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate using OAuth credentials."""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            
            SCOPES = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.send',
                'https://www.googleapis.com/auth/gmail.modify'
            ]
            
            creds = None
            
            # Check for existing token
            if os.path.exists(GMAIL_TOKEN_PATH):
                creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_PATH, SCOPES)
            
            # Refresh or create new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(GMAIL_CREDENTIALS_PATH):
                        print("❌ Gmail credentials not found. See gmail_integration_guide.md")
                        return
                    flow = InstalledAppFlow.from_client_secrets_file(GMAIL_CREDENTIALS_PATH, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for next run
                with open(GMAIL_TOKEN_PATH, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('gmail', 'v1', credentials=creds)
            print("✅ Gmail authenticated successfully!")
            
        except ImportError:
            print("❌ Missing dependencies. Run: pip install google-auth google-auth-oauthlib google-api-python-client")
        except Exception as e:
            print(f"❌ Gmail auth failed: {e}")
    
    def get_unread_emails(self, max_results=10):
        """Fetch unread emails from inbox."""
        if not self.service:
            return []
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX', 'UNREAD'],
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                email_data = self.service.users().messages().get(
                    userId='me', id=msg['id'], format='full'
                ).execute()
                
                headers = email_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                # Get body
                body = ""
                if 'parts' in email_data['payload']:
                    for part in email_data['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            break
                elif 'body' in email_data['payload'] and 'data' in email_data['payload']['body']:
                    body = base64.urlsafe_b64decode(email_data['payload']['body']['data']).decode('utf-8')
                
                emails.append({
                    'id': msg['id'],
                    'subject': subject,
                    'from': sender,
                    'date': date,
                    'snippet': email_data.get('snippet', ''),
                    'body': body[:500]  # Truncate for safety
                })
            
            return emails
            
        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
            return []
    
    def send_email(self, to, subject, body):
        """Send an email."""
        if not self.service:
            return False
        
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            print(f"✅ Email sent to {to}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send: {e}")
            return False
    
    def mark_as_read(self, message_id):
        """Mark an email as read."""
        if not self.service:
            return False
        
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            print(f"❌ Failed to mark as read: {e}")
            return False


if __name__ == "__main__":
    # Run this to authenticate for the first time
    commander = EmailCommander()
    
    if commander.service:
        print("\n📬 Fetching unread emails...")
        emails = commander.get_unread_emails(5)
        for email in emails:
            print(f"  - {email['from']}: {email['subject']}")
