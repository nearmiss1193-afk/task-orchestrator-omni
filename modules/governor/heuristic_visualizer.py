
# 📈 Core Script: heuristic_visualizer.py
# Purpose: Visualize heuristic evolution vs system performance.

import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Local Environment Setup
load_dotenv()
url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def get_supabase():
    if not url or not key:
        raise ValueError("Supabase credentials missing in .env")
    return create_client(url, key)

# --- STEP 1: Fetch Data ---
def fetch_data(sb):
    print("Fetching Heuristics...")
    h_res = sb.table('heuristic_rules').select('*').execute()
    h_data = h_res.data if h_res.data else []
    
    print("Fetching Reflections...")
    r_res = sb.table('reflection_parser').select('*').execute()
    r_data = r_res.data if r_res.data else []
    
    return h_data, r_data

# --- STEP 2: Prepare DataFrames ---
def prepare_data(h_data, r_data):
    if not h_data or not r_data:
        print("⚠️ Insufficient data for visualization.")
        return None

    df_h = pd.DataFrame(h_data)
    df_r = pd.DataFrame(r_data)
    
    # Convert timestamps
    df_h['created_at'] = pd.to_datetime(df_h['created_at'])
    df_r['created_at'] = pd.to_datetime(df_r['created_at'])
    
    # Sort
    df_h = df_h.sort_values('created_at')
    df_r = df_r.sort_values('created_at')
    
    # Merge (AsOf) - matching heuristics to the closest following report might be tricky 
    # if timestamps differ widely. 
    # Strategy: Plot Reflections as the base time-series, and overlay Heuristics as events.
    return df_h, df_r

# --- STEP 3: Visualize ---
def visualize(df_h, df_r, output_path="heuristic_trends.png"):
    plt.figure(figsize=(12, 7))
    
    # Plot Metrics
    plt.plot(df_r['created_at'], df_r['avg_gain'], label='Average Gain', color='gold', linewidth=2)
    
    if 'drift_index' in df_r.columns:
        plt.plot(df_r['created_at'], df_r['drift_index'], label='Drift Index', color='crimson', linestyle='--', alpha=0.7)

    # Plot Heuristics Events
    # We map heuristics to their creation time. Y-Position needs to be arbitrary or linked to a metric.
    # We'll rely on time-alignment.
    y_min, y_max = plt.ylim()
    y_event_level = (y_max + y_min) / 2 if y_max != y_min else 0.5
    
    # Let's plot them on the Gain line (interpolate gain at that timestamp) or just markers
    # For simplicity: Vertical lines or markers at heuristic timestamps
    for _, row in df_h.iterrows():
        plt.axvline(x=row['created_at'], color='lime', alpha=0.5, linestyle=':', label='_nolegend_')
        # Add marker
        plt.text(row['created_at'], y_event_level, "★", color='lime', fontsize=12, ha='center')

    plt.title('Imperium: Heuristic Evolution vs. System Performance')
    plt.xlabel('Timeline')
    plt.ylabel('Performance Metrics')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    print(f"Saving plot to {output_path}...")
    plt.savefig(output_path)
    # plt.show() # Uncomment if interactive

# --- STEP 4: Summary ---
def summarize(df_h):
    if df_h.empty: return
    df_h['week'] = df_h['created_at'].dt.to_period('W')
    summary = df_h.groupby('week')['insight'].count().reset_index()
    summary.columns = ['Week', 'New Rules']
    print("\n🧭 Weekly Heuristic Introductions:")
    print(summary.to_string(index=False))

def main():
    try:
        sb = get_supabase()
        h_data, r_data = fetch_data(sb)
        
        result = prepare_data(h_data, r_data)
        if result:
            df_h, df_r = result
            visualize(df_h, df_r)
            summarize(df_h)
            
    except Exception as e:
        print(f"❌ Visualization Failed: {e}")

if __name__ == "__main__":
    main()
