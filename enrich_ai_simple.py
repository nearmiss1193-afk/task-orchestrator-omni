"""
SIMPLE AI ENRICHMENT - Direct Claude Research
Uses Claude AI to research owner info from the web
"""
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

def ai_enrich(company_name, city, state, phone=None):
    """
    Use Claude AI with web search to find owner info
    """
    print(f"\n🤖 AI Research: {company_name} ({city}, {state})")
    
    try:
        # Build a detailed prompt
        prompt = f"""Research this HVAC company and find the owner/CEO contact information:

Company: {company_name}
Location: {city}, {state}
{f'Phone: {phone}' if phone else ''}

Please search the web and find:
1. Owner or CEO name
2. Owner email (if available)
3. Owner direct phone (if available)

Return ONLY in this exact JSON format:
{{
  "name": "First Last",
  "email": "owner@company.com",
  "phone": "+1234567890",
  "title": "Owner"
}}

If you cannot find the information, return:
{{"found": false}}"""

        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            },
            json={
                'model': 'claude-3-5-sonnet-20241022',
                'max_tokens': 500,
                'messages': [{
                    'role': 'user',
                    'content': prompt
                }]
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['content'][0]['text']
            
            print(f"  📝 Claude response: {content[:200]}...")
            
            # Try to parse JSON from response
            import json
            
            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            else:
                # Try to find JSON object
                json_match = re.search(r'\{.*?\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
            
            try:
                result = json.loads(content)
                
                if result.get('found') == False:
                    print(f"  ❌ Claude couldn't find owner info")
                    return None
                
                if result.get('name'):
                    print(f"  ✅ Found: {result.get('name')} ({result.get('title', 'Owner')})")
                    if result.get('email'):
                        print(f"     Email: {result.get('email')}")
                    if result.get('phone'):
                        print(f"     Phone: {result.get('phone')}")
                    
                    return {
                        'name': result.get('name'),
                        'email': result.get('email'),
                        'phone': result.get('phone'),
                        'title': result.get('title', 'Owner'),
                        'source': 'claude_ai'
                    }
            except json.JSONDecodeError:
                print(f"  ⚠️ Could not parse Claude response as JSON")
                
                # Fallback: try to extract name manually
                name_match = re.search(r'"name":\s*"([^"]+)"', content)
                if name_match:
                    return {
                        'name': name_match.group(1),
                        'title': 'Owner',
                        'source': 'claude_ai'
                    }
    
    except Exception as e:
        print(f"  ❌ AI research error: {e}")
    
    return None

# Test function
if __name__ == '__main__':
    # Test with multiple companies
    test_companies = [
        ("JW Plumbing Heating Air", "Los Angeles", "CA", "213-379-5931"),
        ("Gorgis AC Heating", "San Diego", "CA", "619-780-1104"),
        ("Cabrillo Plumbing AC", "San Francisco", "CA", "415-360-0560"),
    ]
    
    print("="*60)
    print("TESTING AI ENRICHMENT")
    print("="*60)
    
    results = []
    for company, city, state, phone in test_companies:
        result = ai_enrich(company, city, state, phone)
        results.append((company, result))
        print()
    
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    
    success = sum(1 for _, r in results if r is not None)
    print(f"\nSuccess Rate: {success}/{len(results)} ({success/len(results)*100:.0f}%)")
    
    for company, result in results:
        if result:
            print(f"✅ {company}: {result.get('name')}")
        else:
            print(f"❌ {company}: No info found")
