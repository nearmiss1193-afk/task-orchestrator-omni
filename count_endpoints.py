
import os
import re

def count_endpoints():
    with open('deploy.py', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    endpoints = re.findall(r'@modal\.fastapi_endpoint', content)
    print(f"Total fastapi_endpoints: {len(endpoints)}")
    
    # Also find function names
    pattern = r'@modal\.fastapi_endpoint.*?\ndef\s+(\w+)'
    names = re.findall(pattern, content, re.DOTALL)
    print(f"Endpoint names: {names}")

if __name__ == "__main__":
    count_endpoints()
