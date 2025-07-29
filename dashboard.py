import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# —————– Load and configure Gemini API —————–
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# —————– Page config: MUST be first Streamlit call —————–
st.set_page_config(page_title="AI & Tech Dashboard", layout="wide")

# —————– Auto-Refresh Every 5 Hours —————–
def auto_refresh(interval_minutes: int = 300):
    interval_ms = interval_minutes * 60 * 1000
    st.markdown(
        f"""
        <script>
            setTimeout(function() {{ window.location.reload(); }}, {interval_ms});
        </script>
        """,
        unsafe_allow_html=True
    )

auto_refresh(300)

# —————– Utility: Gemini Call —————–
def generate_response(prompt: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        resp = model.generate_content(prompt)
        return resp.text.strip() if resp and resp.text else "No content returned."
    except Exception as e:
        return f"Error: {e}"

# —————– UI —————–
st.title("🌐 AI & Tech Dashboard")
st.sidebar.title("Navigate Dashboard")
page = st.sidebar.radio("Select Section", [
    "Overview", "Latest News", "Tech Stack", "Industry Trends"
])

if page == "Overview":
    st.subheader("Dashboard Overview")
    st.markdown(
        "Welcome! Navigate via the sidebar and click buttons to fetch live AI & tech insights."
    )

elif page == "Latest News":
    st.subheader("📰 Latest AI & Tech News")
    prompt = (
        "Provide a concise, updated summary of the latest AI and technology news: "
        "include breakthroughs, new tool launches, and major developments."
    )
    if st.button("Fetch Latest News"):
        with st.spinner("Fetching..."):
            st.write(generate_response(prompt))

elif page == "Tech Stack":
    st.subheader("🧰 Tech Stack Insights")
    prompt = (
        "Summarize the most popular tech stacks in 2025: languages, frameworks, "
        "and cloud platforms, with brief statistics."
    )
    if st.button("Fetch Tech Stack Insights"):
        with st.spinner("Fetching..."):
            st.write(generate_response(prompt))

elif page == "Industry Trends":
    st.subheader("📊 Industry Trends")
    prompt = (
        "Analyze current technology industry trends, including emerging technologies, "
        "market dynamics, and predictions for future innovations."
    )
    if st.button("Fetch Industry Trends"):
        with st.spinner("Fetching..."):
            st.write(generate_response(prompt))

st.markdown("---\n_Created with ❤️ using Google Gemini API_")
