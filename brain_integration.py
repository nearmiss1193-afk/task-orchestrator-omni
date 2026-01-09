"""
brain_integration.py
====================
Reusable module for all agents to connect to the Brain (system_memory).

USAGE:
    from brain_integration import pre_task_fetch, post_task_learn

    # Before starting a task
    context = pre_task_fetch()
    print(f"Brain says: {context}")

    # After completing a task
    post_task_learn(
        task_name="Sent follow-up email",
        outcome="success",
        learnings="Shorter subject lines get better opens.",
        agent_name="SarahSpartan"
    )
"""

import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def pre_task_fetch():
    """
    Fetch the latest operational buffer from the Brain.
    Call this BEFORE starting any significant task.
    
    Returns:
        str: The current operational directives, or a default message.
    """
    if not DATABASE_URL:
        return "[BRAIN OFFLINE] No DATABASE_URL configured."
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT value FROM system_memory WHERE key = 'operational_buffer';")
        result = cur.fetchone()
        conn.close()
        
        if result:
            return result[0]
        else:
            return "[BRAIN EMPTY] No operational buffer found."
    
    except Exception as e:
        return f"[BRAIN ERROR] {e}"


def post_task_learn(task_name, outcome, learnings, agent_name="unknown"):
    """
    Write learnings to the agent_learnings table.
    Call this AFTER completing any significant task.
    
    Args:
        task_name (str): Name/description of the task.
        outcome (str): 'success', 'failure', 'partial', etc.
        learnings (str): What was learned from this task.
        agent_name (str): Name of the agent (default: 'unknown').
    
    Returns:
        bool: True if successful, False otherwise.
    """
    if not DATABASE_URL:
        print("[BRAIN OFFLINE] Cannot write learnings.")
        return False
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO agent_learnings (task, outcome, learnings, agent_name, created_at)
            VALUES (%s, %s, %s, %s, NOW());
        """, (task_name, outcome, learnings, agent_name))
        
        conn.commit()
        conn.close()
        print(f"🧠 Learning recorded: {task_name} ({outcome})")
        return True
    
    except Exception as e:
        print(f"[BRAIN ERROR] Failed to write learning: {e}")
        return False


def get_recent_learnings(limit=10):
    """
    Retrieve recent learnings from the agent_learnings table.
    
    Args:
        limit (int): Maximum number of records to return.
    
    Returns:
        list: List of learning records.
    """
    if not DATABASE_URL:
        return []
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            SELECT task, outcome, learnings, agent_name, created_at
            FROM agent_learnings
            ORDER BY created_at DESC
            LIMIT %s;
        """, (limit,))
        
        results = cur.fetchall()
        conn.close()
        
        return [
            {
                "task": r[0],
                "outcome": r[1],
                "learnings": r[2],
                "agent_name": r[3],
                "created_at": r[4].strftime("%Y-%m-%d %H:%M:%S") if r[4] else None
            }
            for r in results
        ]
    
    except Exception as e:
        print(f"[BRAIN ERROR] Failed to fetch learnings: {e}")
        return []


# Quick test if run directly
if __name__ == "__main__":
    print("🧠 Brain Integration Module Test")
    print("=" * 40)
    
    print("\n1. Pre-Task Fetch:")
    context = pre_task_fetch()
    print(context[:500] + "..." if len(context) > 500 else context)
    
    print("\n2. Post-Task Learn:")
    post_task_learn(
        task_name="Brain Integration Test",
        outcome="success",
        learnings="The brain_integration module is working correctly.",
        agent_name="SystemTest"
    )
    
    print("\n3. Recent Learnings:")
    learnings = get_recent_learnings(3)
    for l in learnings:
        print(f"  - {l['task']} ({l['outcome']})")
