"""Get full memory diagnostic output"""
from supabase import create_client
from dotenv import load_dotenv
import os
import json

load_dotenv('.env')
load_dotenv('.secrets/secrets.env')

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
sb = create_client(url, key)

# Get all records
r = sb.table('customer_memory').select('*').execute()

# Write to file AND print
output_lines = []
output_lines.append("=" * 70)
output_lines.append("ALL CUSTOMER_MEMORY RECORDS")
output_lines.append("=" * 70)

for row in r.data:
    output_lines.append(json.dumps(row, indent=2, default=str))
    output_lines.append("-" * 40)

output_lines.append("")
output_lines.append("=" * 70)
output_lines.append(f"TOTAL RECORDS: {len(r.data)}")
output_lines.append("=" * 70)

output = "\n".join(output_lines)
print(output)

# Also save to file
with open("memory_output.txt", "w") as f:
    f.write(output)
