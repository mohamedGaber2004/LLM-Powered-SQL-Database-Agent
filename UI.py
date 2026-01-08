import streamlit as st
import requests
import pandas as pd
from typing import Optional, Dict, Any

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 30  # seconds

# Page config
st.set_page_config(
    page_title="🤖 AI SQL Query Generator",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for colorful & animated style
st.markdown("""
<style>
/* Page background: gradient from deep purple to soft pink */
body {
    background: linear-gradient(135deg, #1e3c72, #2a5298, #ff758c, #ff7eb3);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    font-family: 'Segoe UI', sans-serif;
    color: #f0f0f0;
}

/* Gradient animation */
@keyframes gradientBG {
    0%{background-position:0% 50%}
    50%{background-position:100% 50%}
    100%{background-position:0% 50%}
}

/* Button styles */
.stButton>button {
    background: linear-gradient(to right, #ff416c, #ff4b2b);
    color: white;
    font-weight: bold;
    border-radius: 10px;
    padding: 0.6rem 1rem;
    transition: transform 0.2s, box-shadow 0.2s;
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0px 5px 15px rgba(0,0,0,0.3);
}

/* Text area styles */
textarea {
    border-radius: 8px !important;
    border: 2px solid #ff416c !important;
    padding: 0.5rem !important;
    transition: box-shadow 0.2s;
    background-color: #1f1f2e;
    color: #fff;
}
textarea:focus {
    box-shadow: 0 0 10px #ff4b2b !important;
}

/* Expander animation & color */
div[data-testid="stExpander"] > button {
    font-weight: bold;
    background: linear-gradient(to right, #36d1dc, #5b86e5);
    color: white;
    border-radius: 8px;
    transition: transform 0.2s;
}
div[data-testid="stExpander"] > button:hover {
    transform: scale(1.05);
}

/* SQL code box */
.sql-box {
    background-color: rgba(255, 255, 255, 0.1);
    border-left: 5px solid #ff416c;
    padding: 1rem;
    border-radius: 8px;
    font-family: monospace;
    font-size: 0.95rem;
    color: #fff;
}

/* Metrics styles */
.stMetric > div {
    background: linear-gradient(to right, #36d1dc, #5b86e5);
    color: white !important;
    border-radius: 10px;
    padding: 0.5rem;
    text-align: center;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# --- Backend check ---
def check_backend_health() -> bool:
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def query_database(prompt: str) -> Optional[Dict[str, Any]]:
    """Generate and execute in one API call"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/query/",
            json={"prompt": prompt},
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", "Unknown error")
            st.error(f"❌ Query failed: {error_detail}")
            return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Cannot connect to backend.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

# --- Session state ---
if "generated_sql" not in st.session_state:
    st.session_state.generated_sql = None
if "execution_results" not in st.session_state:
    st.session_state.execution_results = None
if "query_history" not in st.session_state:
    st.session_state.query_history = []

# --- Sidebar ---
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    backend_status = check_backend_health()
    if backend_status:
        st.success("✅ Backend connected")
    else:
        st.error("❌ Backend offline")

    st.divider()
    st.markdown("### 📝 Example Queries")
    examples = [
        "Show all users registered in the last 30 days",
        "Count total orders by status",
        "Find top 10 customers by total spending",
        "List products with low inventory (< 10 units)",
        "Calculate average order value by month"
    ]
    selected_example = st.selectbox("Choose an example:", [""] + examples)
    if st.button("Use Example") and selected_example:
        st.session_state.user_input = selected_example
    
    st.divider()
    if st.button("🗑️ Clear History"):
        st.session_state.query_history = []
        st.session_state.generated_sql = None
        st.session_state.execution_results = None
        st.rerun()

# --- Main content ---
st.markdown("# 🤖 AI-Powered SQL Query Generator")
st.markdown("Enter your query in natural language and get SQL results instantly!")

user_input = st.text_area(
    "💬 Your Query:",
    value=st.session_state.get("user_input", ""),
    height=100,
    placeholder="Example: Show me all active users who made purchases last month"
)

if st.button("🚀 Generate & Execute") and user_input:
    with st.spinner("✨ Processing your query..."):
        result = query_database(user_input)
        if result:
            st.session_state.generated_sql = result.get("query")
            st.session_state.execution_results = result
            st.session_state.query_history.append({
                "prompt": user_input,
                "sql": result.get("query"),
                "row_count": result.get("row_count", 0)
            })
            st.success("✅ Query executed successfully!")

# --- Display results ---
if st.session_state.execution_results:
    results = st.session_state.execution_results
    
    st.divider()
    st.markdown("## 📊 Query Results")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Rows Returned", results.get("row_count", 0))
    with col2:
        st.metric("Status", results.get("status", "unknown").upper())
    
    data = results.get("results", [])
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="query_results.csv",
            mime="text/csv"
        )
    else:
        st.info("No rows returned")
    
    # Animated & colorful SQL box
    if st.session_state.generated_sql:
        with st.expander("🛠️ View Generated SQL"):
            st.markdown(f"<div class='sql-box'>{st.session_state.generated_sql}</div>", unsafe_allow_html=True)

    if results.get("optimization_tips"):
        with st.expander("💡 Optimization Tips"):
            st.info(results.get("optimization_tips"))

# --- Query history ---
if st.session_state.query_history:
    st.divider()
    st.markdown("## 📜 Query History")
    for i, item in enumerate(reversed(st.session_state.query_history[-5:])):
        with st.expander(f"Query {len(st.session_state.query_history) - i}: {item['prompt'][:50]}..."):
            st.markdown(f"**Prompt:** {item['prompt']}")
            st.code(item['sql'], language="sql")
            st.caption(f"Returned {item['row_count']} rows")
