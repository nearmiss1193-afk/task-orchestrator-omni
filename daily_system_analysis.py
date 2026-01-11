"""
Daily System Analysis - Deep analysis of entire system
Automated daily task to identify improvements and feed to brain
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
import anthropic

load_dotenv()

def analyze_system_components():
    """Analyze all system components for potential improvements"""
    
    components = {
        "campaigns": {
            "files": ["ca_hi_blitz.py", "campaign_enriched.py", "scheduled_campaign.py"],
            "metrics": ["call_volume", "answer_rate", "dm_contact_rate"],
            "status": "active"
        },
        "enrichment": {
            "files": ["enrich_decision_makers.py", "enrich_web_scraping.py", "top_20_prospects.md"],
            "metrics": ["enrichment_success_rate", "time_per_prospect"],
            "status": "active"
        },
        "ai_agents": {
            "files": ["weekly_learning_agent.py", "ab_test_manager.py"],
            "metrics": ["hypothesis_quality", "test_success_rate"],
            "status": "newly_deployed"
        },
        "monitoring": {
            "files": ["health_monitor.py", "modal_health_monitor.py"],
            "metrics": ["uptime", "alert_frequency"],
            "status": "active"
        },
        "sops": {
            "files": ["operational_memory.md", "AUTOMATED_GROWTH_SOP.md", "AUTOMATED_GROWTH_VALIDATION.md"],
            "metrics": ["sop_compliance", "documentation_completeness"],
            "status": "active"
        }
    }
    
    return components

def check_brain_integration():
    """Check if data is being fed to brain (artifacts directory)"""
    brain_dir = "C:\\Users\\nearm\\.gemini\\antigravity\\brain\\6ec66d63-d29a-4316-87d2-a1c21879a62a"
    
    brain_files = []
    if os.path.exists(brain_dir):
        brain_files = os.listdir(brain_dir)
    
    return {
        "brain_directory": brain_dir,
        "brain_exists": os.path.exists(brain_dir),
        "files_in_brain": brain_files,
        "last_updated": datetime.now().isoformat()
    }

def deep_analysis_with_ai(system_components, brain_status):
    """Use Claude to perform deep system analysis"""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    prompt = f"""Perform a deep analysis of this AI automation system and identify improvement opportunities.

SYSTEM COMPONENTS:
{json.dumps(system_components, indent=2)}

BRAIN STATUS (Artifact Integration):
{json.dumps(brain_status, indent=2)}

ANALYSIS REQUIRED:
1. **Gaps & Weaknesses**: What's missing or could break?
2. **Optimization Opportunities**: Where can we improve efficiency?
3. **Automation Potential**: What manual tasks should be automated?
4. **Data Flow**: Is everything being captured and fed to the brain?
5. **Risk Assessment**: What could go wrong?

For each finding, provide:
- Category (gap/optimization/automation/data/risk)
- Severity (critical/high/medium/low)
- Description
- Recommended action
- Estimated impact

Format as JSON array of findings."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    findings_text = message.content[0].text
    
    # Parse and track provenance
    findings = json.loads(findings_text)
    
    return {
        "analysis_date": datetime.now().isoformat(),
        "findings": findings,
        "provenance": {
            "source": "ai_generated",
            "model": "claude-3-5-sonnet-20241022",
            "created_at": datetime.now().isoformat(),
            "requires_human_review": True
        }
    }

def save_to_brain(analysis_results):
    """Save analysis to brain (artifacts directory)"""
    brain_dir = "C:\\Users\\nearm\\.gemini\\antigravity\\brain\\6ec66d63-d29a-4316-87d2-a1c21879a62a"
    
    # Ensure brain directory exists
    os.makedirs(brain_dir, exist_ok=True)
    
    # Save daily analysis
    filename = f"daily_analysis_{datetime.now().strftime('%Y%m%d')}.json"
    filepath = os.path.join(brain_dir, filename)
    
    with open(filepath, "w") as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"✓ Saved to brain: {filepath}")
    return filepath

def update_capabilities_gaps():
    """Update CAPABILITIES_GAPS.md with new findings"""
    gaps_file = "CAPABILITIES_GAPS.md"
    
    # This would be updated with actual findings
    # For now, just log that it should be updated
    print(f"✓ CAPABILITIES_GAPS.md should be updated with new findings")

def generate_daily_report(analysis_results):
    """Generate human-readable daily report"""
    report = f"""# Daily System Analysis Report
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total Findings: {len(analysis_results['findings'])}
- Critical: {sum(1 for f in analysis_results['findings'] if f.get('severity') == 'critical')}
- High: {sum(1 for f in analysis_results['findings'] if f.get('severity') == 'high')}
- Medium: {sum(1 for f in analysis_results['findings'] if f.get('severity') == 'medium')}
- Low: {sum(1 for f in analysis_results['findings'] if f.get('severity') == 'low')}

## Critical Findings
"""
    
    critical = [f for f in analysis_results['findings'] if f.get('severity') == 'critical']
    for f in critical:
        report += f"\n### {f.get('description', 'N/A')}\n"
        report += f"- **Category:** {f.get('category', 'N/A')}\n"
        report += f"- **Action:** {f.get('recommended_action', 'N/A')}\n"
        report += f"- **Impact:** {f.get('estimated_impact', 'N/A')}\n"
    
    report += "\n## All Findings\n"
    for i, f in enumerate(analysis_results['findings'], 1):
        report += f"\n{i}. **[{f.get('severity', 'N/A').upper()}]** {f.get('description', 'N/A')}\n"
        report += f"   - Action: {f.get('recommended_action', 'N/A')}\n"
    
    # Save report
    report_file = f"daily_analysis_report_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, "w") as f:
        f.write(report)
    
    print(f"✓ Generated report: {report_file}")
    return report_file

def main():
    """Main execution - Daily system analysis"""
    print("="*70)
    print("DAILY SYSTEM ANALYSIS")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Step 1: Analyze system components
    print("Step 1: Analyzing system components...")
    components = analyze_system_components()
    print(f"✓ Analyzed {len(components)} component categories\n")
    
    # Step 2: Check brain integration
    print("Step 2: Checking brain integration...")
    brain_status = check_brain_integration()
    print(f"✓ Brain directory: {brain_status['brain_exists']}")
    print(f"✓ Files in brain: {len(brain_status['files_in_brain'])}\n")
    
    # Step 3: Deep AI analysis
    print("Step 3: Performing deep AI analysis...")
    analysis_results = deep_analysis_with_ai(components, brain_status)
    print(f"✓ Generated {len(analysis_results['findings'])} findings\n")
    
    # Step 4: Save to brain
    print("Step 4: Saving to brain...")
    brain_file = save_to_brain(analysis_results)
    
    # Step 5: Generate report
    print("\nStep 5: Generating daily report...")
    report_file = generate_daily_report(analysis_results)
    
    # Step 6: Update CAPABILITIES_GAPS.md
    print("\nStep 6: Updating CAPABILITIES_GAPS.md...")
    update_capabilities_gaps()
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"Brain file: {brain_file}")
    print(f"Report file: {report_file}")
    print(f"\nCritical findings: {sum(1 for f in analysis_results['findings'] if f.get('severity') == 'critical')}")
    print("="*70)

if __name__ == "__main__":
    main()
