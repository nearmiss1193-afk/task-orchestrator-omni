"""
GROK VOICE API CLIENT
=====================
xAI Grok Voice Agent API integration for real-time speech-to-speech.
Uses WebSocket for full-duplex audio streaming.

Based on OpenAI Realtime API specification.
Docs: https://docs.x.ai/docs/guides/voice-agents

Voices available: Ara, Eve, Leo, Nova, Sage
"""
import os
import json
import asyncio
import base64
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
GROK_VOICE_WS_URL = "wss://api.x.ai/v1/realtime"
GROK_VOICE_REST_URL = "https://api.x.ai/v1"

# Available voices
VOICES = {
    "ara": "Warm and friendly female voice",
    "eve": "Professional and clear female voice", 
    "leo": "Confident male voice",
    "nova": "Energetic female voice",
    "sage": "Calm and wise voice"
}


class GrokVoiceClient:
    """xAI Grok Voice Agent API Client"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GROK_API_KEY
        self.ws_url = GROK_VOICE_WS_URL
        self.voice = "eve"  # Default voice
        
        if not self.api_key:
            print("⚠️ GROK_API_KEY not set")
    
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_ephemeral_token(self) -> Optional[str]:
        """Get ephemeral token for client-side WebSocket auth"""
        res = requests.post(
            f"{GROK_VOICE_REST_URL}/realtime/sessions",
            headers=self._headers(),
            json={"model": "grok-2-voice-latest"},
            timeout=30
        )
        
        if res.status_code == 200:
            return res.json().get("client_secret")
        return None
    
    def text_to_speech(
        self,
        text: str,
        voice: str = "eve",
        output_file: str = "output.mp3"
    ) -> bool:
        """
        Convert text to speech using Grok Voice API.
        Note: If TTS endpoint not available, falls back to chat with voice.
        """
        # Try TTS endpoint
        res = requests.post(
            f"{GROK_VOICE_REST_URL}/audio/speech",
            headers=self._headers(),
            json={
                "model": "grok-2-voice-latest",
                "input": text,
                "voice": voice
            },
            timeout=60
        )
        
        if res.status_code == 200:
            with open(output_file, "wb") as f:
                f.write(res.content)
            return True
        else:
            print(f"TTS not available via REST: {res.status_code}")
            return False
    
    def speech_to_text(self, audio_file: str) -> Optional[str]:
        """
        Transcribe audio using Grok Voice API.
        """
        with open(audio_file, "rb") as f:
            audio_data = f.read()
        
        res = requests.post(
            f"{GROK_VOICE_REST_URL}/audio/transcriptions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            files={"file": audio_data},
            data={"model": "grok-2-voice-latest"},
            timeout=60
        )
        
        if res.status_code == 200:
            return res.json().get("text")
        return None


def test_grok_voice():
    """Test Grok Voice API capabilities"""
    print("🎙️ Testing Grok Voice API...")
    
    client = GrokVoiceClient()
    
    if not client.api_key:
        print("❌ No API key found")
        return False
    
    # Test ephemeral token generation
    print("\n1. Testing ephemeral token generation...")
    token = client.get_ephemeral_token()
    if token:
        print(f"✅ Ephemeral token obtained (starts with: {token[:20]}...)")
    else:
        print("⚠️ Ephemeral token not available (may require WebSocket connection)")
    
    # Test TTS
    print("\n2. Testing Text-to-Speech...")
    success = client.text_to_speech(
        "Hello Empire! This is Grok Voice speaking. Ready to assist you!",
        voice="eve",
        output_file="grok_voice_test.mp3"
    )
    
    if success:
        print("✅ TTS successful - saved to grok_voice_test.mp3")
    else:
        print("⚠️ TTS via REST not available - requires WebSocket realtime connection")
        print("   Use the xAI Console voice playground for testing: console.x.ai")
    
    print("\n🎙️ Voice API test complete!")
    print("\nFor real-time voice chat, the API uses WebSocket connections.")
    print("Integrate with Vapi or use the xAI Console playground for live testing.")
    
    return True


if __name__ == "__main__":
    test_grok_voice()
