import os
import json
import requests
from typing import Dict, Any, Optional

class AICouncil:
    """
    The AI COUNCIL BROKER
    Routes tasks to the optimal LLM expert based on intent.
    Supported Experts: Claude (Human Tone), GPT-4o (Logic), Gemini Flash (Speed), Grok (Real-time).
    """

    def __init__(self):
        self.keys = {
            "google": os.environ.get("GOOGLE_API_KEY"),
            "openai": os.environ.get("OPENAI_API_KEY"),
            "anthropic": os.environ.get("ANTHROPIC_API_KEY"),
            "xai": os.environ.get("XAI_API_KEY")  # Grok
        }

    async def get_expert(self, intent: str, prompt: str, system_prompt: str = "") -> str:
        """Routes prompt to the council member best suited for the job."""
        
        if intent == "outreach_copy":
            # Claude 3.5 Sonnet is the King of Human Tone
            return await self._call_claude(prompt, system_prompt)
            
        elif intent == "logical_planning":
            # GPT-4o for complex branching
            return await self._call_gpt4o(prompt, system_prompt)
            
        elif intent == "real_time_web":
            # Grok-1 (or Perplexity fallback) for live trends
            return await self._call_grok(prompt, system_prompt)
            
        else:
            # Gemini 1.5 Flash for high-speed, low-cost poller/analysis
            return await self._call_gemini_flash(prompt, system_prompt)

    async def _call_claude(self, prompt: str, system: str) -> str:
        """Consult Anthropic Claude 3.5 Sonnet."""
        import anthropic
        client = anthropic.Anthropic(api_key=self.keys["anthropic"])
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    async def _call_gpt4o(self, prompt: str, system: str) -> str:
        """Consult OpenAI GPT-4o."""
        import openai
        client = openai.OpenAI(api_key=self.keys["openai"])
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    async def _call_gemini_flash(self, prompt: str, system: str) -> str:
        """Consult Google Gemini 1.5 Flash."""
        import google.generativeai as genai
        genai.configure(api_key=self.keys["google"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            f"{system}\n\n{prompt}" if system else prompt
        )
        return response.text

    async def _call_grok(self, prompt: str, system: str) -> str:
        """Consult xAI Grok (using requests)."""
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.keys['xai']}"
        }
        payload = {
            "model": "grok-1",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

# Global instance for v2 modules
council = AICouncil()
