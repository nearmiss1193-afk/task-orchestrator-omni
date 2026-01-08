import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client
import stripe

# Load Config
load_dotenv()
st.set_page_config(page_title="Empire Unified Command", layout="wide", page_icon="⚡")

# Initialize Connections
@st.cache_resource
def init_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)

supabase = init_supabase()

# Stripe Init
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Title
st.title("⚡ Empire Sovereign Command")

# Sidebar
st.sidebar.header("Control Panel")
view_mode = st.sidebar.radio("View Mode", ["Live Operations", "Campaign Manager", "Financials"])

if not supabase:
    st.error("Supabase Credentials Missing. Check .env")
    st.stop()

# --- LIVE OPERATIONS VIEW ---
if view_mode == "Live Operations":
    st.header("🦅 Live Agent Status")
    
    # 1. Agent Presence
    try:
        presence_data = supabase.table('agent_presence').select("*").execute().data
        if presence_data:
            df_presence = pd.DataFrame(presence_data)
            st.dataframe(df_presence, use_container_width=True)
        else:
            st.info("No Agents Online")
    except Exception as e:
        st.error(f"Error fetching presence: {e}")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Task Queue")
        # Fetch pending tasks
        tasks = supabase.table('tasks_queue').select("*").order('created_at', desc=True).limit(10).execute().data
        if tasks:
            for task in tasks:
                status_color = "🟢" if task['status'] == 'completed' else "🟡" if task['status'] == 'processing' else "🔴"
                st.write(f"{status_color} **{task['task_type']}**: {task['status']}")
                with st.expander("Details"):
                    st.json(task)
        else:
            st.caption("Queue Empty")

    with col2:
        st.subheader("📡 System Telemetry")
        try:
            logs = supabase.table('system_logs').select("*").order('created_at', desc=True).limit(20).execute().data
            if logs:
                df_logs = pd.DataFrame(logs)
                # Reorder columns for readability
                st.dataframe(
                    df_logs[['created_at', 'level', 'message', 'context']], 
                    use_container_width=True,
                    column_config={
                        "created_at": st.column_config.DatetimeColumn("Time", format="D MMM, HH:mm:ss"),
                        "level": "Lvl",
                        "message": "Event",
                        "context": "Data"
                    }
                )
            else:
                st.caption("No logs found.")
        except Exception as e:
            st.error(f"Log Error: {e}")

# --- CAMPAIGN MANAGER VIEW ---
elif view_mode == "Campaign Manager":
    st.header("🎯 Campaign Manager")
    
    with st.form("new_campaign"):
        c_name = st.text_input("Campaign Name")
        c_type = st.selectbox("Type", ["outbound_call", "email_blast"])
        submitted = st.form_submit_button("Create Draft")
        
        if submitted:
            supabase.table('campaigns').insert({
                "name": c_name,
                "type": c_type,
                "status": "draft"
            }).execute()
            st.success("Campaign Created")

    st.divider()
    st.subheader("Active Campaigns")
    campaigns = supabase.table('campaigns').select("*").execute().data
    if campaigns:
        st.dataframe(campaigns)

# --- FINANCIALS VIEW ---
elif view_mode == "Financials":
    st.header("💰 Financial Performance")
    
    if not stripe.api_key:
        st.warning("Stripe API Key missing")
    else:
        try:
            # Simulated financial metrics for dashboard (Real Stripe calls can be slow/rate-limited)
            balance = stripe.Balance.retrieve()
            pending = balance['pending'][0]['amount'] / 100
            available = balance['available'][0]['amount'] / 100
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Pending Balance", f"${pending:,.2f}")
            col2.metric("Available Payout", f"${available:,.2f}")
            col3.metric("Platform Fees (MTD)", "$1,250.00") # Placeholder
            
            st.subheader("Recent Connect Transfers")
            # In a real app we would query stripe.Transfer.list(limit=5)
            st.info("Connect Transfer data would utilize `stripe.Transfer.list()` here.")
            
        except Exception as e:
            st.error(f"Stripe Error: {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.text(f"System Time: {time.strftime('%H:%M:%S')}")
