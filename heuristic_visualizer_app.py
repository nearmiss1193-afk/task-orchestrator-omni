import streamlit as st
import pandas as pd
import supabase
import plotly.express as px
from datetime import datetime
import os

# --- CONFIG ---
# Auto-detect from environment or use placeholders
SUPABASE_URL = os.environ.get("SUPABASE_URL", "<your-supabase-url>")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "<your-supabase-key>")

def get_supabase_client():
    return supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    sb = get_supabase_client()
except Exception as e:
    st.error(f"Failed to connect to Supabase: {e}")
    st.stop()

st.set_page_config(page_title="Imperium Heuristic Visualizer", layout="wide")

# --- TITLE ---
st.title("🧭 Imperium Heuristic Evolution Dashboard")
st.markdown("Visualize heuristic changes, reflection data, and performance trends across epochs.")

# --- DATA FETCH ---
@st.cache_data(ttl=600)
def load_data():
    try:
        heuristics = sb.table('heuristic_rules').select('*').execute().data or []
        reflections = sb.table('reflection_parser').select('*').execute().data or []
    except Exception as e:
        st.warning(f"Could not fetch data (tables might be empty or missing): {e}")
        return pd.DataFrame(), pd.DataFrame()

    df_h = pd.DataFrame(heuristics)
    df_r = pd.DataFrame(reflections)
    if not df_h.empty and 'created_at' in df_h:
        df_h['created_at'] = pd.to_datetime(df_h['created_at'])
    if not df_r.empty and 'created_at' in df_r:
        df_r['created_at'] = pd.to_datetime(df_r['created_at'])
    return df_h, df_r

df_h, df_r = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")
if not df_r.empty:
    min_date = df_r['created_at'].min().date()
    max_date = df_r['created_at'].max().date()
else:
    min_date = datetime.now().date()
    max_date = datetime.now().date()

start_date = st.sidebar.date_input("Start Date", value=min_date)
end_date = st.sidebar.date_input("End Date", value=max_date)

# Filter by date range
if not df_r.empty:
    # Ensure datetime comparison compatibility
    mask = (df_r['created_at'].dt.date >= start_date) & (df_r['created_at'].dt.date <= end_date)
    df_r = df_r[mask]

# --- SECTION: PERFORMANCE TRENDS ---
st.subheader("📈 System Performance Over Time")
if not df_r.empty:
    # Check if columns exist
    cols = ['avg_gain','drift_index','redundancy_efficiency']
    existing_cols = [c for c in cols if c in df_r.columns]
    
    if existing_cols:
        fig = px.line(df_r, x='created_at', y=existing_cols,
                      labels={'value':'Metric Value','created_at':'Date'},
                      title='System Gain, Drift, and Redundancy Efficiency Over Time')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Performance metrics (avg_gain, etc.) not found in reflection data.")
else:
    st.info("No reflection data available yet.")

# --- SECTION: HEURISTIC TIMELINE ---
st.subheader("🔄 Heuristic Introductions Timeline")
if not df_h.empty:
    df_h_weekly = df_h.copy()
    df_h_weekly['week'] = df_h_weekly['created_at'].dt.to_period('W').astype(str)
    # Ensure 'insight' exists
    if 'insight' in df_h_weekly.columns:
        weekly_counts = df_h_weekly.groupby('week')['insight'].count().reset_index()
        bar_fig = px.bar(weekly_counts, x='week', y='insight', title='Weekly Heuristic Introductions', color='insight', color_continuous_scale='viridis')
        st.plotly_chart(bar_fig, use_container_width=True)
    else:
        st.warning("Column 'insight' not found in heuristic rules.")
else:
    st.warning("No heuristic introductions logged yet.")

# --- SECTION: LESSONS & NEXT DIRECTIVES ---
st.subheader("🧾 Latest Insights & Directives")
if not df_r.empty:
    latest = df_r.sort_values('created_at', ascending=False).head(1).iloc[0]
    st.markdown(f"**Epoch ID:** {latest.get('epoch_id', 'N/A')}")
    st.markdown(f"**Lessons Learned:** {latest.get('lesson_summary', 'N/A')}")
    st.markdown(f"**Next Epoch Focus:** {latest.get('next_epoch_focus', 'N/A')}")
else:
    st.info("Waiting for first Reflection Cycle report...")

# --- FOOTER ---
st.markdown("— Built for Imperium Sovereign Oversight, v38.5 —")
