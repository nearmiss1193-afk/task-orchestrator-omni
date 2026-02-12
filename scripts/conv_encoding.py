f = open('scripts/memory_diag.txt', 'r', encoding='utf-8-sig')
content = f.read()
f.close()
# Write clean version
with open('scripts/memory_diag_clean.txt', 'w', encoding='utf-8') as f2:
    f2.write(content)
