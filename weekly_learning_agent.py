"""
Weekly Learning Agent - Analyzes campaign data and generates hypotheses
CRITICAL: Includes human review gate to prevent model collapse
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import anthropic

load_dotenv()

# CRITICAL: Data provenance tracking
def track_data_provenance(data, source_type):
    """Track origin of all data to prevent model collapse"""
    return {
        "data": data,
        "provenance": {
            "source": source_type,  # "human_generated", "ai_generated", "api_data"
            "created_at": datetime.now().isoformat(),
            "validated_by": "pending_human_review" if source_type == "ai_generated" else "system",
            "collection_method": "automated"
        }
    }

def analyze_weekly_metrics():
    """Aggregate and analyze past week's campaign data"""
    # Load campaign metrics from past 7 days
    metrics = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        try:
            with open(f"campaign_metrics_{date}.json", "r") as f:
                daily_data = json.load(f)
                metrics.append(track_data_provenance(daily_data, "human_generated"))
        except FileNotFoundError:
            continue
    
    if not metrics:
        print("No metrics found for analysis")
        return None
    
    # Calculate aggregates
    total_calls = sum(m['data'].get('total_calls', 0) for m in metrics)
    total_answers = sum(m['data'].get('answered_calls', 0) for m in metrics)
    total_dm_contacts = sum(m['data'].get('dm_contacts', 0) for m in metrics)
    
    answer_rate = total_answers / total_calls if total_calls > 0 else 0
    dm_contact_rate = total_dm_contacts / total_answers if total_answers > 0 else 0
    
    return {
        "total_calls": total_calls,
        "answer_rate": answer_rate,
        "dm_contact_rate": dm_contact_rate,
        "metrics_count": len(metrics),
        "data_provenance": [m['provenance'] for m in metrics]
    }

def generate_hypotheses_with_ai(weekly_summary):
    """Generate hypotheses using Claude - MARKED AS AI-GENERATED"""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    prompt = f"""Analyze this weekly campaign data and generate 3 specific, testable hypotheses for improvement:

Weekly Summary:
- Total Calls: {weekly_summary['total_calls']}
- Answer Rate: {weekly_summary['answer_rate']:.1%}
- DM Contact Rate: {weekly_summary['dm_contact_rate']:.1%}

For each hypothesis, provide:
1. The hypothesis statement
2. Why you think this might work
3. How to test it (A/B test design)
4. Expected impact

Format as JSON array."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    hypotheses_text = message.content[0].text
    
    # CRITICAL: Mark as AI-generated and require human review
    hypotheses = json.loads(hypotheses_text)
    for h in hypotheses:
        h['source'] = 'ai_generated'
        h['requires_human_approval'] = True
        h['created_at'] = datetime.now().isoformat()
        h['confidence_score'] = 0.0  # Will be set by human reviewer
    
    return track_data_provenance(hypotheses, "ai_generated")

def save_for_human_review(hypotheses_data):
    """Save hypotheses for human review - CRITICAL GATE"""
    review_file = f"pending_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(review_file, "w") as f:
        json.dump({
            "status": "PENDING_HUMAN_REVIEW",
            "created_at": datetime.now().isoformat(),
            "hypotheses": hypotheses_data['data'],
            "provenance": hypotheses_data['provenance'],
            "review_instructions": "Please review each hypothesis and set confidence_score (0-1). Approve by setting 'approved': true"
        }, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"HUMAN REVIEW REQUIRED")
    print(f"{'='*60}")
    print(f"File: {review_file}")
    print(f"Hypotheses generated: {len(hypotheses_data['data'])}")
    print(f"\nPlease review and approve before deployment.")
    print(f"{'='*60}\n")
    
    # Send email notification
    send_review_notification(review_file, hypotheses_data)
    
    return review_file

def send_review_notification(review_file, hypotheses_data):
    """Send email to owner for hypothesis review"""
    from resend import Resend
    
    resend = Resend(api_key=os.getenv("RESEND_API_KEY"))
    
    hypotheses_summary = "\n".join([
        f"{i+1}. {h['hypothesis']}" 
        for i, h in enumerate(hypotheses_data['data'])
    ])
    
    resend.emails.send({
        "from": "system@aiserviceco.com",
        "to": "owner@aiserviceco.com",
        "subject": "Weekly Learning Agent: Hypotheses Require Review",
        "html": f"""
        <h2>New Hypotheses Generated - Human Review Required</h2>
        <p><strong>File:</strong> {review_file}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h3>Hypotheses:</h3>
        <pre>{hypotheses_summary}</pre>
        
        <p><strong>Action Required:</strong> Review file and approve before deployment.</p>
        <p><em>This is a critical safety gate to prevent model collapse.</em></p>
        """
    })

def main():
    """Main execution - Weekly learning cycle with human review gate"""
    print("Starting Weekly Learning Agent...")
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Step 1: Analyze weekly metrics
    print("Step 1: Analyzing weekly metrics...")
    weekly_summary = analyze_weekly_metrics()
    
    if not weekly_summary:
        print("No data to analyze. Exiting.")
        return
    
    print(f"✓ Analyzed {weekly_summary['metrics_count']} days of data")
    print(f"  - Total Calls: {weekly_summary['total_calls']}")
    print(f"  - Answer Rate: {weekly_summary['answer_rate']:.1%}")
    print(f"  - DM Contact Rate: {weekly_summary['dm_contact_rate']:.1%}\n")
    
    # Step 2: Generate hypotheses (AI)
    print("Step 2: Generating hypotheses with AI...")
    hypotheses_data = generate_hypotheses_with_ai(weekly_summary)
    print(f"✓ Generated {len(hypotheses_data['data'])} hypotheses\n")
    
    # Step 3: CRITICAL - Save for human review
    print("Step 3: Saving for human review (CRITICAL GATE)...")
    review_file = save_for_human_review(hypotheses_data)
    
    print(f"\n✓ Weekly learning cycle complete")
    print(f"✓ Awaiting human approval: {review_file}")
    print(f"\nNOTE: Hypotheses will NOT be deployed until human review is complete.")

if __name__ == "__main__":
    main()
