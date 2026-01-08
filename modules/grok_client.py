"""
GROK API CLIENT MODULE
======================
xAI Grok integration for the Empire Unified system.
Enables advanced reasoning, image generation, and live search capabilities.

API Docs: https://docs.x.ai/
Base URL: https://api.x.ai/v1
Compatible with OpenAI SDK (just change base_url)
"""
import os
import json
import requests
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Configuration
GROK_API_KEY = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
GROK_BASE_URL = "https://api.x.ai/v1"

class GrokClient:
    """xAI Grok API Client for the Empire Unified system"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GROK_API_KEY
        self.base_url = GROK_BASE_URL
        
        if not self.api_key:
            print("⚠️ GROK_API_KEY not set. Get one at https://x.ai/api")
    
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "grok-3-latest",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        tools: Optional[List[Dict]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to Grok.
        
        Models available:
        - grok-3-latest (most capable)
        - grok-3-mini-latest (faster, cheaper)
        - grok-3-fast-latest (optimized for speed)
        - grok-vision-beta (image understanding)
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        if tools:
            payload["tools"] = tools
        
        res = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self._headers(),
            json=payload,
            timeout=60
        )
        
        if res.status_code == 200:
            return res.json()
        else:
            return {"error": res.status_code, "message": res.text}
    
    def generate_image(
        self,
        prompt: str,
        model: str = "grok-2-image",
        n: int = 1,
        size: str = "1024x1024"
    ) -> Dict[str, Any]:
        """Generate images using Grok's image generation model"""
        payload = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size
        }
        
        res = requests.post(
            f"{self.base_url}/images/generations",
            headers=self._headers(),
            json=payload,
            timeout=120
        )
        
        if res.status_code == 200:
            return res.json()
        else:
            return {"error": res.status_code, "message": res.text}
    
    def analyze_image(
        self,
        image_url: str,
        prompt: str = "Describe this image in detail.",
        model: str = "grok-vision-beta"
    ) -> Dict[str, Any]:
        """Analyze an image using Grok's vision capabilities"""
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ]
        
        return self.chat_completion(messages, model=model)
    
    def list_models(self) -> Dict[str, Any]:
        """List all available Grok models"""
        res = requests.get(
            f"{self.base_url}/models",
            headers=self._headers(),
            timeout=30
        )
        
        if res.status_code == 200:
            return res.json()
        else:
            return {"error": res.status_code, "message": res.text}
    
    def ask(self, question: str, system_prompt: Optional[str] = None) -> str:
        """Simple helper to ask Grok a question and get a text response"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": question})
        
        result = self.chat_completion(messages)
        
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        elif "error" in result:
            return f"Error: {result['message']}"
        else:
            return str(result)


# --- EMPIRE UNIFIED INTEGRATION ---

def grok_analyze_call_transcript(transcript: str, client: Optional[GrokClient] = None) -> Dict[str, Any]:
    """Use Grok to deeply analyze a call transcript and extract learnings"""
    if client is None:
        client = GrokClient()
    
    system_prompt = """You are an expert sales coach analyzing call transcripts. 
    Extract the following in JSON format:
    - customer_sentiment: positive/neutral/negative
    - objections_raised: list of specific objections
    - successful_rebuttals: what worked to overcome objections
    - missed_opportunities: what the rep could have said differently
    - key_pain_points: what problems the customer mentioned
    - buying_signals: indications of interest
    - recommended_followup: next best action
    - coaching_notes: actionable feedback for the sales rep
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Analyze this call transcript:\n\n{transcript}"}
    ]
    
    result = client.chat_completion(messages, model="grok-3-latest")
    
    if "choices" in result:
        response = result["choices"][0]["message"]["content"]
        # Try to parse as JSON
        try:
            # Find JSON block in response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "{" in response:
                json_str = response[response.index("{"):response.rindex("}")+1]
            else:
                json_str = response
            return json.loads(json_str)
        except:
            return {"raw_analysis": response}
    
    return result


def grok_generate_prospect_email(prospect_info: Dict[str, str], client: Optional[GrokClient] = None) -> str:
    """Use Grok to generate a personalized prospect outreach email"""
    if client is None:
        client = GrokClient()
    
    system_prompt = """You are a witty, sharp sales copywriter. 
    Write personalized outreach emails that are:
    - Conversational, not corporate
    - Specific to the prospect's business
    - Value-focused with a clear CTA
    - Under 150 words
    - No generic "I hope this email finds you well" openings
    """
    
    prompt = f"""Write a sales email for this prospect:
    Company: {prospect_info.get('company', 'Unknown')}
    Industry: {prospect_info.get('industry', 'Service Business')}
    Pain Points: {prospect_info.get('pain_points', 'Missed calls, slow response times')}
    Our Solution: AI-powered phone automation that never misses a lead
    CTA: Book a demo call
    """
    
    return client.ask(prompt, system_prompt)


def test_grok_connection():
    """Test the Grok API connection"""
    print("🧠 Testing Grok API connection...")
    
    client = GrokClient()
    
    if not client.api_key:
        print("❌ No API key found. Set GROK_API_KEY in .env")
        print("   Get your key at: https://x.ai/api")
        return False
    
    # Test with a simple question
    response = client.ask("Say 'Hello Empire!' if you can hear me.")
    
    if "error" in response.lower():
        print(f"❌ Connection failed: {response}")
        return False
    else:
        print(f"✅ Grok says: {response}")
        return True


if __name__ == "__main__":
    test_grok_connection()
