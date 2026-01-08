
# Remove Rick Roll video link from hvac_landing.html
file_path = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\apps\client-portal\public\hvac_landing.html"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Convert lines to find the rickroll index specifically
for i, line in enumerate(lines):
    if "dQw4w9WgXcQ" in line:
        print(f"Found Rick Roll at line {i+1}")
        lines[i] = '                <div class="video-placeholder" onclick="alert(\'Full system demo video coming soon!\')">\n'
        break

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Successfully removed Rick Roll.")
