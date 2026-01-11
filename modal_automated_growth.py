"""
Modal Deployment - Automated Growth System
Deploys all critical safeguards and daily analysis to Modal cloud
"""

import modal

# Create Modal app
app = modal.App("automated-growth-system")

# Create image with all dependencies
image = modal.Image.debian_slim().pip_install(
    "anthropic",
    "scipy",
    "resend",
    "python-dotenv",
    "requests"
)

# Mount secrets
secrets = [
    modal.Secret.from_name("anthropic-api-key"),
    modal.Secret.from_name("resend-api-key"),
    modal.Secret.from_name("supabase-credentials")
]

# ============================================================================
# DAILY SYSTEM ANALYSIS - Runs every day at 8 PM EST
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 20 * * *"),  # 8 PM daily (UTC: 0 20)
    timeout=600
)
def daily_system_analysis():
    """
    Analyzes entire system daily
    - Identifies gaps and improvements
    - Feeds results to brain
    - Generates daily report
    """
    import sys
    import os
    
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(__file__))
    
    from daily_system_analysis import main
    
    print("Starting Daily System Analysis...")
    main()
    print("Daily System Analysis complete!")

# ============================================================================
# WEEKLY LEARNING AGENT - Runs every Sunday at 8 PM EST
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 20 * * 0"),  # 8 PM Sundays (UTC: 0 20, day 0)
    timeout=600
)
def weekly_learning_agent():
    """
    Analyzes weekly campaign data
    - Generates hypotheses with AI
    - Requires human review (CRITICAL GATE)
    - Sends email notification
    """
    import sys
    import os
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    from weekly_learning_agent import main
    
    print("Starting Weekly Learning Agent...")
    main()
    print("Weekly Learning Agent complete!")

# ============================================================================
# HEALTH MONITOR - Runs every 3 hours
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 */3 * * *"),  # Every 3 hours
    timeout=300
)
def health_monitor():
    """
    Monitors system health
    - Checks all endpoints
    - Verifies API connectivity
    - Sends alerts if issues detected
    """
    import sys
    import os
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    from health_monitor import main
    
    print("Starting Health Monitor...")
    main()
    print("Health Monitor complete!")

# ============================================================================
# MANUAL TRIGGERS (for testing)
# ============================================================================

@app.function(image=image, secrets=secrets)
def test_daily_analysis():
    """Manual trigger for testing daily analysis"""
    daily_system_analysis.local()

@app.function(image=image, secrets=secrets)
def test_weekly_learning():
    """Manual trigger for testing weekly learning"""
    weekly_learning_agent.local()

@app.function(image=image, secrets=secrets)
def test_health_check():
    """Manual trigger for testing health monitor"""
    health_monitor.local()

# ============================================================================
# DEPLOYMENT INFO
# ============================================================================

@app.local_entrypoint()
def main():
    """Display deployment info"""
    print("="*70)
    print("AUTOMATED GROWTH SYSTEM - MODAL DEPLOYMENT")
    print("="*70)
    print("\nScheduled Functions:")
    print("  1. Daily System Analysis  - Every day at 8 PM EST")
    print("  2. Weekly Learning Agent  - Every Sunday at 8 PM EST")
    print("  3. Health Monitor         - Every 3 hours")
    print("\nManual Triggers:")
    print("  - modal run modal_automated_growth.py::test_daily_analysis")
    print("  - modal run modal_automated_growth.py::test_weekly_learning")
    print("  - modal run modal_automated_growth.py::test_health_check")
    print("\nDeployment:")
    print("  modal deploy modal_automated_growth.py")
    print("="*70)

if __name__ == "__main__":
    main()
