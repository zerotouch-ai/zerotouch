import streamlit as st
import psycopg2 
import pandas as pd
import plotly.express as px
import json
import time
import os

# config
st.set_page_config(
    page_title="zerotouch",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "port": os.getenv("POSTGRES_PORT", 5432),
    "dbname": os.getenv("POSTGRES_DB", "zerotouch"),
    "user": os.getenv("POSTGRES_USER", "zerotouch"),
    "password": os.getenv("POSTGRES_PASSWORD", "zerotouch")
}

# DB Connection
def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def fetch_incidents() -> pd.DataFrame:
    try:
        conn = get_connection()
        df = pd.read_sql("""
            SELECt
               id,
               timestamp,
               anomaly_type,
               anomaly_score,
               metrics,
               action_taken,
               reasoning,
               resolution_time,
               resolved
            From incidents
            ORDER BY timestamp DESC
            LIMIT 100
        """, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return pd.DataFrame()
    
def fetch_stats() -> dict:
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM incidents")
        total = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM incidents WHERE resolved = TRUE;")
        resolved = cur.fetchone()[0]

        cur.execute("SELECT AVG(resolution_time) FROM incidents;")
        avg_time = cur.fetchone()[0] or 0

        cur.execute("SELECT AVG(anomaly_score) FROM incidents;")
        avg_score = cur.fetchone()[0] or 0

        cur.close()
        conn.close()

        return {
            "total": total,
            "resolved": resolved,
            "avg_resolution_time": round(avg_time, 2),
            "avg_anomaly_score": round(avg_score, 4)
        }
    except Exception:
        return{"total": 0, "resolved": 0, "avg_resolution_time": 0, "avg_anomaly_score": 0}
    
# styling
st.markdown("""
<style>
    .main { background-color: #0a0e1a; }
    .block-container { padding-top: 1rem; }
    .metric-card {
        background: linear-gradient(135deg, #1a2035, #1f2d4a);
        border: 1px solid #2a3f6f;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .anomaly-badge {
        background-color: #ff4444;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold
    }
    .resolved-badge {
        background-color: #00cc66;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    h1, h2, h3 {color: #4da6ff !important; }
</style>
""", unsafe_allow_html=True)

# Heaeder
st.markdown("""
<div style='text-align:center; padding: 20px 0;'>
            <h1 style='font-size: 3rem; color: #4da6ff;'>⚡ Zerotouch </h1>
            <p style='color: #899bb; font-size: 1.1rem; '> Zero Human intervention. Fully Autonomous.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar contros
refresh = st.sidebar.slider("Auto-refresh (seconds)", 5, 60, 10)
auto_refresh= st.sidebar.checkbox("Enable auto-refresh", value=True)

# state box
stats = fetch_stats()
col1, col2, col3, col4= st.columns(4)

with col1:
    st.metric("Total Incidents", stats["total"])
with col2:
    st.metric("Auto-Resolved", stats["resolved"])
with col3:
    st.metric("Avg Resolution Time", f"{stats['avg_resolution_time']}s")
with col4:
    st.metric("Avg Anomaly Score", stats["avg_anomaly_score"])

st.divider()

# Fetch Data
df = fetch_incidents()

if df.empty:
    st.info("No incidets yet. System is montoring......")
else:
    col_left, col_right = st.columns(2)


    with col_left:
        st.subheader("Anomaly Score Over Time")
        fig = px.line(
            df.sort_values("timestamp"),
            x="timestamp",
            y="anomaly_score",
            color_discrete_sequence=["#4da6ff"]
        )
        fig.update_layout(
            paper_bgcolor="#0a0e1a",
            plot_bgcolor="#0a0e1a",
            font_color="#8899bb"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Incidents by Type")
        type_counts = df["anomaly_type"].value_counts().reset_index()
        type_counts.columns = ["type", "count"]
        fig2 = px.pie(
            type_counts,
            names="type",
            values="count",
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig2.update_layout(
            paper_bgcolor="#0a0e1a",
            font_color="#8899bb",
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Resolution Time Bar
        st.subheader("Resolution Time per Incident (seconds)")
        fig3 = px.bar(
            df.sort_values("timestamp"),
            x="timestamp",
            y="resolution_time",
            color="anomaly_type",
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig3.update_layout(
            paper_bgcolor="#0a0e1a",
            plot_bgcolor="#0a0e1a",
            font_color="#8899bb",
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.divider()

# Incident Table
st.subheader("Incidents History")
for _, row in df.iterrows():
    with st.expander(
        f"{'🔴' if not row['resolved'] else '✅'} "
        f"{row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - "
        f"{row['anomaly_type']} (score: {row['anomaly_score']:.4f})"
    ):
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("**Action Taken:**", row['action_taken'])
            st.write("**Resolution Time:**", f"{row['resolution_time']:.2f}s")
            st.write("**Resolved:**", "✅ yes" if row ["resolved"] else "❌ No")
        with col_b:
            st.write("**Agent Reasoning:**")
            st.info(row["reasoning"] or "No reasoning logged.")

        if row["metrics"]:
            st.write("**Metrics at time of anomaly:**")
            metrics = row["metrics"] if isinstance(row["metrics"], dict) else json.loads(row["metrics"])
            st.json(metrics)

# Auto-refresh (safe pattern)
if auto_refresh:
    time.sleep(refresh)
    st.rerun()