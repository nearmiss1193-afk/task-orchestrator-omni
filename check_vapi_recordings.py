import os, requests, json

def get_ghl_contacts():
    token = os.getenv('GHL_AGENCY_API_TOKEN')
    location = os.getenv('GHL_LOCATION_ID')
    if not token or not location:
        raise RuntimeError('GHL credentials not set')
    url = f'https://rest.gohighlevel.com/v1/contacts?locationId={location}'
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get('contacts', [])

def check_recordings():
    contacts = get_ghl_contacts()
    recordings = []
    for c in contacts:
        # Assuming a custom field "CallRecording" holds the URL
        rec = c.get('customFields', [])
        for field in rec:
            if field.get('name') == 'CallRecording' and field.get('value'):
                recordings.append({
                    'contactId': c.get('id'),
                    'name': c.get('firstName'),
                    'email': c.get('email'),
                    'recordingUrl': field.get('value')
                })
    return recordings

def main():
    try:
        recs = check_recordings()
        if recs:
            print('Found Vapi call recordings in GHL:')
            print(json.dumps(recs, indent=2))
        else:
            print('No Vapi call recordings found in GHL.')
    except Exception as e:
        print('Error checking recordings:', e)

if __name__ == '__main__':
    main()
