
from modules.email_command import EmailCommander
import datetime
import sys

def scan_inbox():
    print("🕵️ Deep Scanning Inbox (to file)...")
    commander = EmailCommander()
    
    if not commander.service:
        print("❌ Auth Failed")
        return

    output = []
    output.append("🕵️ Deep Scanning Inbox (owner@aiserviceco.com)...")

    # List messages (INBOX only, include read and unread)
    try:
        results = commander.service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            maxResults=20
        ).execute()
        
        messages = results.get('messages', [])
        output.append(f"📬 Found {len(messages)} recent messages.\n")
        
        for msg in messages:
            try:
                email = commander.service.users().messages().get(
                    userId='me', id=msg['id'], format='full'
                ).execute()
                
                headers = email['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
                snippet = email.get('snippet', '')
                
                output.append(f"--------------------------------------------------")
                output.append(f"ID: {msg['id']}")
                output.append(f"FROM: {sender}")
                output.append(f"DATE: {date}")
                output.append(f"SUBJ: {subject}")
                output.append(f"BODY: {snippet}...")
                output.append(f"--------------------------------------------------\n")
            except Exception as e:
                output.append(f"Error reading msg {msg['id']}: {e}")
            
    except Exception as e:
        output.append(f"Error list: {e}")

    with open("inbox_audit_utf8.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    print("✅ Scan Complete. Check inbox_audit_utf8.txt")

if __name__ == "__main__":
    scan_inbox()
