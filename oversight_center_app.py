import streamlit as st
import pandas as pd
import plotly.express as px
import os
from supabase import create_client
from datetime import datetime
import time

# --- CONFIG ---
st.set_page_config(page_title="Sovereign Oversight Center", layout="wide", page_icon="👁️")
st.title("👁️ Sovereign Oversight Center")
st.markdown("*The All-Seeing Eye of the Empire*")

# --- DATABASE CONNECTION ---
@st.cache_resource
def init_db():
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

try:
    supabase = init_db()
except:
    st.error("Supabase Connection Failed. Check Environment Variables.")
    st.stop()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🕹️ Controls")
refresh_rate = st.sidebar.slider("Refresh Rate (s)", 5, 60, 30)

# --- METRIC LOGIC (EGI) ---
def calculate_egi():
    # 1. Lead Count
    leads = supabase.table("contacts_master").select("id", count="exact").execute()
    count = leads.count or 0
    
    # 2. Conversion Estimate (Mock or Real)
    # Using 'client' status or similar
    convs = supabase.table("contacts_master").select("id", count="exact").eq("status", "client").execute()
    conversions = convs.count or 0
    conv_rate = (conversions / count) if count > 0 else 0.0
    
    # 3. Uptime/Health (from Logs)
    logs = supabase.table("brain_logs").select("level").order("timestamp", desc=True).limit(50).execute()
    errs = len([x for x in logs.data if x['level'] in ['CRITICAL', 'ERR']])
    uptime = 1.0 - (errs / 50)
    
    # Formula: (Uptime*30) + (Conv*50) + (Count*0.1)
    egi = (uptime * 30) + (conv_rate * 50) + (count * 0.1)
    return egi, uptime, conv_rate, count

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Main Board", "🗣️ Voice Intelligence", "🏹 Campaign Pulse", "🕹️ Command"])

with tab1:
    # Key Metrics
    egi, uptime, conv, count = calculate_egi()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Economic Gain Index (EGI)", f"{egi:.1f}", delta=f"{uptime*100:.0f}% Health")
    c2.metric("Total Leads", count)
    c3.metric("Conversion Rate", f"{conv:.1%}")
    c4.metric("Active Agents", "5") # Spartan, Spear, Nexus, Director, Governor

    st.divider()
    
    # Log Stream
    st.subheader("📝 Live Stream (Brain Logs)")
    logs = supabase.table("brain_logs").select("*").order("timestamp", desc=True).limit(20).execute()
    df_logs = pd.DataFrame(logs.data)
    if not df_logs.empty:
        st.dataframe(df_logs[['timestamp', 'level', 'message']], use_container_width=True)

with tab2:
    st.subheader("🗣️ Nexus Voice Analysis")
    # Fetch Voice Logs
    v_logs = supabase.table("voice_logs").select("*").order("analyzed_at", desc=True).limit(50).execute()
    if v_logs.data:
        df_voice = pd.DataFrame(v_logs.data)
        
        c1, c2 = st.columns(2)
        with c1:
            # Sentiment Pie
            fig_sent = px.pie(df_voice, names='sentiment_tone', title="Caller Sentiment Distribution")
            st.plotly_chart(fig_sent, use_container_width=True)
            
        with c2:
            # Confidence vs Outcome
            fig_conf = px.bar(df_voice, x='outcome', y='confidence_index', color='sentiment_tone', title="Confidence by Outcome")
            st.plotly_chart(fig_conf, use_container_width=True)
            
        st.dataframe(df_voice, use_container_width=True)
    else:
        st.info("No Voice Data Logged Yet.")

with tab3:
    st.subheader("🏹 Campaign Evolution")
    # Fetch Campaign Performance
    c_perf = supabase.table("campaign_performance").select("*").order("date", desc=True).limit(30).execute()
    if c_perf.data:
        df_camp = pd.DataFrame(c_perf.data)
        
        # Line Chart: Pos vs Neg
        fig_evol = px.line(df_camp, x='date', y=['positive', 'negative'], title="Response Sentiment Trends")
        st.plotly_chart(fig_evol, use_container_width=True)
    else:
        st.info("No Campaign Data Logged Yet.")

with tab4:
    st.subheader("👮 Governor Override")
    st.write("Push a direct instruction to the Internal Supervisor loop.")
    
    cmd = st.text_input("Enter Instruction (e.g., 'REBOOT SPARTAN', 'PAUSE MARKETING')")
    if st.button("Transmit Order"):
        if cmd:
            payload = {
                "level": "CMD",
                "message": f"[USER OVERRIDE] {cmd}",
                "timestamp": datetime.now().isoformat()
            }
            try:
                supabase.table("brain_logs").insert(payload).execute()
                st.success("Command Transmitted to Nervous System.")
            except Exception as e:
                st.error(f"Transmission Failed: {e}")

# Auto-Refresh
time.sleep(refresh_rate)
st.rerun()
