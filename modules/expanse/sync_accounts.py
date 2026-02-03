import sqlite3
import os
import argparse
import json
import zipfile
from datetime import datetime

DB_PATH = "ai_accounts.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Platforms table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS platforms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        base_url TEXT NOT NULL
    )
    ''')
    
    # Accounts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform_id INTEGER,
        email TEXT NOT NULL,
        plan_tier TEXT,
        last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (platform_id) REFERENCES platforms (id)
    )
    ''')
    
    # Conversations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        external_id TEXT UNIQUE,
        title TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY (account_id) REFERENCES accounts (id)
    )
    ''')
    
    # Projects table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT
    )
    ''')
    
    # Project-Conversation junction table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS project_conversations (
        project_id INTEGER,
        conversation_id INTEGER,
        PRIMARY KEY (project_id, conversation_id),
        FOREIGN KEY (project_id) REFERENCES projects (id),
        FOREIGN KEY (conversation_id) REFERENCES conversations (id)
    )
    ''')
    
    # Seed platforms
    platforms = [
        ('OpenAI', 'https://chat.openai.com'),
        ('Anthropic', 'https://claude.ai'),
        ('Gemini', 'https://gemini.google.com')
    ]
    cursor.executemany('INSERT OR IGNORE INTO platforms (name, base_url) VALUES (?, ?)', platforms)
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def get_platform_id(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM platforms WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def ensure_account(platform_name, email):
    platform_id = get_platform_id(platform_name)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM accounts WHERE platform_id = ? AND email = ?", (platform_id, email))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO accounts (platform_id, email) VALUES (?, ?)", (platform_id, email))
        conn.commit()
        account_id = cursor.lastrowid
    else:
        account_id = row[0]
    conn.close()
    return account_id

def process_openai_export(zip_path, email):
    account_id = ensure_account('OpenAI', email)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        if 'conversations.json' in z.namelist():
            with z.open('conversations.json') as f:
                data = json.load(f)
                count = 0
                for conv in data:
                    # Using keys identified from the actual file
                    external_id = conv.get('uuid') or conv.get('id')
                    title = conv.get('name') or conv.get('title') or conv.get('summary')
                    create_time = conv.get('created_at') or conv.get('create_time')
                    update_time = conv.get('updated_at') or conv.get('update_time')
                    
                    # Handle both float timestamps and ISO strings
                    if isinstance(create_time, (int, float)):
                        ct = datetime.fromtimestamp(create_time).isoformat()
                    else:
                        ct = create_time
                        
                    if isinstance(update_time, (int, float)):
                        ut = datetime.fromtimestamp(update_time).isoformat()
                    else:
                        ut = update_time
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO conversations (account_id, external_id, title, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (account_id, external_id, title, ct, ut))
                    count += 1
                conn.commit()
                print(f"Imported {count} conversations for {email} (OpenAI)")
    conn.close()

def process_claude_export(json_path, email):
    account_id = ensure_account('Anthropic', email)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        count = 0
        for conv in data:
            external_id = conv.get('uuid')
            title = conv.get('name')
            create_time = conv.get('created_at')
            update_time = conv.get('updated_at')
            
            cursor.execute('''
                INSERT OR REPLACE INTO conversations (account_id, external_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (account_id, external_id, title, create_time, update_time))
            count += 1
        conn.commit()
        print(f"Imported {count} conversations for {email} (Claude)")
    conn.close()

def process_gemini_export(zip_path, email):
    account_id = ensure_account('Gemini', email)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        count = 0
        for name in z.namelist():
            # Gemini takeout files are usually in 'Gemini/Chat name.json' or similar
            if name.endswith('.json') and not name.startswith('__MACOSX'):
                with z.open(name) as f:
                    try:
                        data = json.load(f)
                        # Gemini export JSON format can vary, but usually has a list of messages
                        # We'll treat the filename or a specific field as the title
                        external_id = name # Fallback to filename as ID
                        title = os.path.basename(name).replace('.json', '')
                        
                        # Check if it's a legitimate chat file
                        if isinstance(data, list) and len(data) > 0:
                            # Try to find a date in the first message
                            create_time = data[0].get('create_time')
                            cursor.execute('''
                                INSERT OR REPLACE INTO conversations (account_id, external_id, title, created_at)
                                VALUES (?, ?, ?, ?)
                            ''', (account_id, external_id, title, create_time))
                            count += 1
                        elif isinstance(data, dict) and 'messages' in data:
                            create_time = data.get('create_time')
                            cursor.execute('''
                                INSERT OR REPLACE INTO conversations (account_id, external_id, title, created_at)
                                VALUES (?, ?, ?, ?)
                            ''', (account_id, external_id, title, create_time))
                            count += 1
                    except Exception as e:
                        print(f"Skipping {name}: {e}")
                        
        conn.commit()
        print(f"Imported {count} conversations for {email} (Gemini)")
    conn.close()

def categorize_projects():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Define some keyword-based projects
    project_keywords = {
        'Sonic Expanse': ['sonic', 'expanse', 'music', 'sound'],
        '10 Mil Project': ['10 mil', 'million', 'finance', 'project'],
        'AI Development': ['agent', 'bot', 'code', 'python', 'api'],
        'Personal/Idea': ['idea', 'journal', 'plan', 'thought']
    }
    
    for project_name, keywords in project_keywords.items():
        cursor.execute("INSERT OR IGNORE INTO projects (name) VALUES (?)", (project_name,))
        cursor.execute("SELECT id FROM projects WHERE name = ?", (project_name,))
        project_id = cursor.fetchone()[0]
        
        # Find matches in conversation titles
        query = "SELECT id, title FROM conversations WHERE " + " OR ".join(["title LIKE ?" for _ in keywords])
        params = [f"%{k}%" for k in keywords]
        cursor.execute(query, params)
        matches = cursor.fetchall()
        
        for conv_id, title in matches:
            cursor.execute("INSERT OR IGNORE INTO project_conversations (project_id, conversation_id) VALUES (?, ?)", (project_id, conv_id))
            
    conn.commit()
    print("Conversations categorized into projects.")
    conn.close()

def extract_personality():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Find conversations that likely contain personality/preference info
    cursor.execute("SELECT title FROM conversations WHERE title LIKE '%personality%' OR title LIKE '%preference%' OR title LIKE '%instruction%'")
    rows = cursor.fetchall()
    
    personality_content = "# Personality and Preferences\n\n"
    if rows:
        personality_content += "## Identified Conversations\n"
        for row in rows:
            personality_content += f"- {row[0]}\n"
    else:
        personality_content += "No specific personality-themed chats found yet. These are extracted from titles mentioning 'personality' or 'preferences'.\n"
        
    with open("personality.md", "w", encoding="utf-8") as f:
        f.write(personality_content)
    
    print("Personality markers extracted to personality.md")
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync AI account data.")
    parser.add_argument("--init", action="store_true", help="Initialize the database")
    parser.add_argument("--import-openai", help="Path to OpenAI export zip")
    parser.add_argument("--import-claude", help="Path to Claude export json")
    parser.add_argument("--import-gemini", help="Path to Gemini export zip")
    parser.add_argument("--email", help="Email associated with the account")
    parser.add_argument("--categorize", action="store_true", help="Categorize conversations into projects")
    args = parser.parse_args()
    
    if args.init or not os.path.exists(DB_PATH):
        init_db()
        
    if args.import_openai:
        if not args.email:
            print("Error: --email is required for import")
        else:
            process_openai_export(args.import_openai, args.email)
            
    if args.import_claude:
        if not args.email:
            print("Error: --email is required for import")
        else:
            process_claude_export(args.import_claude, args.email)
            
    if args.import_gemini:
        if not args.email:
            print("Error: --email is required for import")
        else:
            process_gemini_export(args.import_gemini, args.email)
            
    if args.categorize:
        categorize_projects()
        extract_personality()
