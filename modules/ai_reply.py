
import os
import requests
import json

def generate_sarah_reply(incoming_subject, incoming_body, sender_name):
    """
    Generates a reply from 'Sarah' using Grok (xAI).
    """
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        return "Error: No API Key"

    prompt = f"""
    Role: You are Sarah, Senior Growth Strategist at Empire Unified (AI Service Co).
    Task: Write a short, professional, and helpful email reply to a prospect.
    Tone: Friendly, concise, confident, no fluff.
    
    Incoming Email from: {sender_name}
    Subject: {incoming_subject}
    Body:
    {incoming_body}
    
    Instructions:
    - If they are interested, offer a time to chat or a 14-day free trial.
    - If they are angry, apologize and offer to remove them.
    - If they have a question, answer it briefly.
    - Sign off as "Sarah".
    - Do NOT include subject lines in your output, just the body.
    """

    try:
        resp = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "messages": [
                    {"role": "system", "content": "You are a helpful sales assistant named Sarah."},
                    {"role": "user", "content": prompt}
                ],
                "model": "grok-beta",
                "stream": False,
                "temperature": 0.7
            }
        )
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content'].strip()
        else:
            return f"Error generating reply: {resp.text}"
    except Exception as e:
        return f"Error: {e}"
