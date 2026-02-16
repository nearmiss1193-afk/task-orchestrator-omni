import os
import requests
import re
import json

def parse_manus(url):
    print(f"Parsing {url}...")
    try:
        r = requests.get(url, timeout=15)
        html = r.text
        
        # Look for lead-like patterns (Business Name, Phone, Metrics)
        # Often Manus output is in a JSON blob or visible text
        # Let's look for phone numbers as anchors
        phones = re.findall(r'\+1\d{10}', html)
        print(f"Found {len(phones)} potential phone numbers")
        
        # Look for PageSpeed scores
        scores = re.findall(r'PageSpeed:\s*(\d+)', html)
        print(f"Found {len(scores)} PageSpeed scores")
        
        # Check if there's a JSON blob
        json_blobs = re.findall(r'\{[^{}]*?"business_name"[^{}]*?\}', html)
        if json_blobs:
            print(f"Found {len(json_blobs)} JSON-like blobs")
            for b in json_blobs[:3]:
                print(f"  Example: {b[:100]}...")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parse_manus("https://manus.im/share/file/78f48b01-143f-443f-ae31-fda5f0a3eb74")
    print("-" * 20)
    parse_manus("https://manus.im/share/file/ab8f93a3-101a-4320-b29c-f6dd02140ca3")
