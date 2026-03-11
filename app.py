import streamlit as st
from agent import ask_agent
from visualizer import generate_chart

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Finance SQL Agent",
    page_icon="📈",
    layout="wide"
)

# ── Styling ───────────────────────────────────────────────────
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput > div > div > input { background-color: #1e2130; color: white; }
    .sql-box { background-color: #1e2130; padding: 1rem; border-radius: 8px;
               border-left: 3px solid #00d4aa; font-family: monospace;
               font-size: 0.85rem; color: #00d4aa; white-space: pre-wrap; }
    </style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────
st.title("📈 Finance SQL Analyst Agent")
st.caption("Powered by LLaMA 3.1 + LangChain · Ask anything about the finance database")

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.header("💡 Example Questions")
    examples = [
        "What are the top 5 most traded stocks?",
        "Show total transaction value by sector",
        "Which stock had the highest average price?",
        "How many BUY vs SELL transactions are there?",
        "Show me the top 5 users by portfolio value",
        "Which sector has the most stocks?",
        "What is the most expensive stock currently?",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.pending_question = ex

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.history = []
        st.rerun()

# ── Session state ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# ── Render chat history ───────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(msg["content"])
            if msg.get("sql"):
                with st.expander("🔍 View SQL Query"):
                    st.markdown(
                        f'<div class="sql-box">{msg["sql"]}</div>',
                        unsafe_allow_html=True
                    )
            if msg.get("dataframe") is not None:
                with st.expander("📊 View Raw Data"):
                    st.dataframe(msg["dataframe"], use_container_width=True)
            if msg.get("chart") is not None:
                st.plotly_chart(msg["chart"], use_container_width=True)
        else:
            st.markdown(msg["content"])

# ── Handle input ──────────────────────────────────────────────
user_input = st.chat_input("Ask a question about the finance data...")

if st.session_state.pending_question:
    user_input = st.session_state.pending_question
    st.session_state.pending_question = None

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            result = ask_agent(user_input, st.session_state.history)

        response_text = result["response_text"]
        sql = result["sql"]
        df = result["dataframe"]
        error = result["error"]

        # Clean response — strip SQL block for display
        import re
        clean_response = re.sub(r"```sql.*?```", "", response_text, flags=re.DOTALL).strip()
        st.markdown(clean_response)

        if error and not sql:
            st.error(f"❌ {error}")

        if sql:
            with st.expander("🔍 View SQL Query"):
                st.markdown(
                    f'<div class="sql-box">{sql}</div>',
                    unsafe_allow_html=True
                )

        chart = None
        if df is not None and not df.empty:
            with st.expander("📊 View Raw Data"):
                st.dataframe(df, use_container_width=True)
            chart = generate_chart(df, user_input)
            if chart:
                st.plotly_chart(chart, use_container_width=True)

    # Save to session
    st.session_state.messages.append({
        "role": "assistant",
        "content": clean_response,
        "sql": sql,
        "dataframe": df,
        "chart": chart
    })
    st.session_state.history.append({
        "user": user_input,
        "assistant": response_text
    })