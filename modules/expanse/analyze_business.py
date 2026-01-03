import sqlite3
import collections

DB_PATH = "ai_accounts.db"

def analyze_business():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Get stats by project
    cursor.execute('''
    SELECT p.name, COUNT(pc.conversation_id) 
    FROM projects p
    LEFT JOIN project_conversations pc ON p.id = pc.project_id
    GROUP BY p.id
    ''')
    project_stats = cursor.fetchall()
    
    # 2. Get most recent conversations to identify current focus
    cursor.execute('''
    SELECT title, created_at 
    FROM conversations 
    ORDER BY created_at DESC 
    LIMIT 20
    ''')
    recent_chats = cursor.fetchall()
    
    # 3. Look for "accomplishment" or "milestone" keywords in titles
    keywords = ['launch', 'finish', 'done', 'complete', 'success', 'reached', 'bought', 'sold', 'deal', 'hire']
    accomplishments = []
    for k in keywords:
        cursor.execute("SELECT title FROM conversations WHERE title LIKE ?", (f"%{k}%",))
        matches = cursor.fetchall()
        accomplishments.extend([m[0] for m in matches])
        
    print("Project Stats:")
    for name, count in project_stats:
        print(f"- {name}: {count} chats")
        
    print("\nRecent Focus:")
    for title, date in recent_chats:
        print(f"- {title} ({date})")
        
    print("\nPotential Accomplishments/Milestones Found:")
    for acc in list(set(accomplishments))[:15]: # Unique and limited
        print(f"- {acc}")
        
    conn.close()

if __name__ == "__main__":
    analyze_business()
