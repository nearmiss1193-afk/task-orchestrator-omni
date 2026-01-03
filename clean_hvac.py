
import os

FILE = "apps/portal/public/landing/hvac.html"

def clean():
    with open(FILE, "rb") as f:
        content = f.read()
    
    # Check for leading whitespace/newlines
    if content.startswith(b'\r\n'):
        print("Found CRLF at start. Removing...")
        content = content[2:]
        with open(FILE, "wb") as f:
            f.write(content)
        print("✅ Cleaned HVAC HTML.")
    elif content.startswith(b'\n'):
         print("Found LF at start. Removing...")
         content = content[1:]
         with open(FILE, "wb") as f:
            f.write(content)
         print("✅ Cleaned HVAC HTML.")
    else:
        print("⚠️ No leading newline found. First 10 bytes:", content[:10])

if __name__ == "__main__":
    clean()
