import os
import zipfile
import resend
import base64
from dotenv import load_dotenv

load_dotenv()

def execute_zip_and_email():
    output_filename = "aiserviceco-full-project-v1.zip"
    recipient = "nearmiss1193@gmail.com"
    subject = "FULL PROJECT ZIP – FOR ARA"
    body = "Here’s the zipped project. Check drift, fix site, return clean code."
    
    # Specific files to include based on Executive Order
    include_files = {
        'public/index.html', 
        'public/features.html', 
        'public/media.html', 
        'public/payment.html', 
        'public/assets/sarah-widget.js', 
        'operational_memory.md', 
        'scripts/traffic_light_automation.py', 
        'brain/0b97dae9-c5c0-4924-8d97-793b59319985/task.md'
    }
    
    # Also include anything in sql/ or snippets/ if relevant to GHL embeds
    extra_dirs = {'sql', 'scripts'}

    print(f"📦 Zipping project: {output_filename}")
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add specific files
        for rel_path in include_files:
            abs_path = os.path.join(os.getcwd(), rel_path)
            if os.path.exists(abs_path):
                zipf.write(abs_path, os.path.basename(rel_path))
        
        # Add sql snippets
        sql_dir = os.path.join(os.getcwd(), 'sql')
        if os.path.exists(sql_dir):
            for file in os.listdir(sql_dir):
                if file.endswith('.sql'):
                    zipf.write(os.path.join(sql_dir, file), os.path.join('sql', file))

    size_mb = os.path.getsize(output_filename) / (1024 * 1024)
    print(f"✅ ZIP COMPLETE - {output_filename} - FILE SIZE: {size_mb:.2f} MB")

    # Send Email
    resend.api_key = os.environ.get("RESEND_API_KEY")
    if not resend.api_key:
        print("❌ RESEND_API_KEY not found in .env")
        return

    print(f"📧 Sending to {recipient}...")
    with open(output_filename, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    try:
        params = {
            "from": "Sovereign AI <automation@aiserviceco.com>",
            "to": [recipient],
            "subject": subject,
            "html": f"<p>{body}</p>",
            "attachments": [
                {
                    "filename": output_filename,
                    "content": encoded,
                }
            ],
        }
        resend.Emails.send(params)
        from datetime import datetime
        print(f"ZIP SENT – {datetime.now().strftime('%I:%M %p')} EST – FILE SIZE: {size_mb:.2f} MB")
    except Exception as e:
        print(f"❌ Email Failed: {e}")

if __name__ == "__main__":
    execute_zip_and_email()
