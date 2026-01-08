
# Fix specific lines in hvac_landing.html that have corrupt icons
file_path = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\apps\client-portal\public\hvac_landing.html"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1-based to 0-based conversion
# Line 1939: Reputation Guard Icon
lines[1938] = '                    <div class="solution-icon">⭐</div>\n'

# Line 1947: Lead Net Icon
lines[1946] = '                    <div class="solution-icon">💰</div>\n'

# Line 2225: Something else Icon
lines[2224] = '                             <div class="funnel-option-icon">✨</div>\n'

# Line 2297: Busy Season Icon
lines[2296] = '                        <div class="funnel-option-icon">☀️</div>\n'

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Successfully patched hvac_landing.html")
