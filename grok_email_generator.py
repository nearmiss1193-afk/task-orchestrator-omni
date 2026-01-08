"""
GROK-POWERED COLD EMAIL GENERATOR (THE SAW)
============================================
Generates hyper-personalized cold emails using Grok's reasoning.
Learns from agent_learnings.json to incorporate successful patterns.

Usage:
    python grok_email_generator.py --company "Homeheart HVAC" --industry "HVAC"
"""
import os
import json
import argparse
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Import Grok client
from modules.grok_client import GrokClient

load_dotenv()

def load_learnings() -> Dict[str, Any]:
    """Load learnings from previous calls for context"""
    try:
        with open("agent_learnings.json", "r") as f:
            return json.load(f)
    except:
        return {}

def generate_cold_email(
    company: str,
    industry: str = "Service Business",
    pain_points: str = "Missed calls, slow lead response",
    decision_maker: str = "Owner",
    campaign_type: str = "initial_outreach"
) -> Dict[str, str]:
    """
    Generate a personalized cold email using Grok.
    Returns dict with subject, body_html, and body_text.
    """
    client = GrokClient()
    learnings = load_learnings()
    
    # Build context from learnings
    objections_context = ""
    if learnings.get("objections_encountered"):
        objections_context = f"\nKnown objections to address: {', '.join(learnings['objections_encountered'][:5])}"
    
    system_prompt = f"""You are a world-class cold email copywriter for an AI automation agency.
Your emails are:
- Conversational, NEVER corporate or salesy
- Specific to the prospect's business
- Under 150 words
- No "I hope this finds you well" or similar fluff
- Include a specific observation about their business
- End with a soft CTA (question, not hard pitch)

Company context:
- We offer AI phone agents that answer calls 24/7
- We help service businesses never miss a lead
- Our AI can book appointments, answer questions, and qualify leads
{objections_context}

Campaign type: {campaign_type}
- initial_outreach: First touch, curiosity-driven
- followup: Reference previous touchpoint
- breakup: Final attempt, create urgency
"""

    user_prompt = f"""Write a cold email for:
Company: {company}
Industry: {industry}
Decision Maker Title: {decision_maker}
Their Pain Points: {pain_points}

Generate:
1. Subject line (max 6 words, curiosity-driven)
2. Email body (HTML formatted with <p> tags)
3. Plain text version

Respond in JSON format:
{{"subject": "...", "body_html": "...", "body_text": "..."}}
"""

    response = client.ask(user_prompt, system_prompt)
    
    # Parse JSON from response
    try:
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "{" in response:
            json_str = response[response.index("{"):response.rindex("}")+1]
        else:
            json_str = response
        
        result = json.loads(json_str)
        return result
    except:
        return {
            "subject": f"Quick question for {company}",
            "body_html": f"<p>{response}</p>",
            "body_text": response
        }


def generate_email_sequence(
    company: str,
    industry: str = "Service Business"
) -> list:
    """Generate a full 3-email sequence for a prospect"""
    sequence = []
    
    campaigns = [
        ("initial_outreach", "Missed calls, slow lead response"),
        ("followup", "Following up on the missed call problem"),
        ("breakup", "Last attempt before moving on")
    ]
    
    for campaign_type, pain_points in campaigns:
        email = generate_cold_email(
            company=company,
            industry=industry,
            pain_points=pain_points,
            campaign_type=campaign_type
        )
        email["campaign_type"] = campaign_type
        sequence.append(email)
    
    return sequence


def main():
    parser = argparse.ArgumentParser(description="Generate cold emails with Grok")
    parser.add_argument("--company", required=True, help="Target company name")
    parser.add_argument("--industry", default="Service Business", help="Industry")
    parser.add_argument("--sequence", action="store_true", help="Generate full 3-email sequence")
    
    args = parser.parse_args()
    
    print(f"🧠 Generating cold email for {args.company}...")
    
    if args.sequence:
        emails = generate_email_sequence(args.company, args.industry)
        for i, email in enumerate(emails, 1):
            print(f"\n--- Email {i}: {email['campaign_type']} ---")
            print(f"Subject: {email['subject']}")
            print(f"\n{email['body_text']}")
    else:
        email = generate_cold_email(args.company, args.industry)
        print(f"\nSubject: {email['subject']}")
        print(f"\n{email['body_text']}")


if __name__ == "__main__":
    main()
