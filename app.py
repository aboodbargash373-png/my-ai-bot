import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="رداد - Raddad Cyber AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. لغة التصميم المستقبلية (Cyberpunk CSS - نظيفة وبدون تداخل)
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 50% 10%, #101426 0%, #080a12 100%);
        color: #e0e6ed;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background: rgba(13, 17, 30, 0.85) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(0, 242, 254, 0.2);
    }
    .cyber-title {
        font-size: 2.4rem !important;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #00c6ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 25px rgba(0, 242, 254, 0.4);
        margin-bottom: 5px;
    }
    .cyber-subtitle {
        text-align: center;
        color: #88a0c0;
        font-size: 0.95rem;
        margin-bottom: 25px;
        letter-spacing: 1px;
    }
    .metrics-container {
        display: flex;
        justify-content: space-around;
        background: rgba(16, 23, 42, 0.6);
        border: 1px solid rgba(0, 242, 254, 0.25);
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 20px;
        backdrop-filter: blur(8px);
    }
    .metric-value { color: #00f2fe; font-weight: bold; font-size: 0.85rem; text-align: center; }
    .metric-label { color: #64748b; font-size: 0.75rem; text-align: center; }
    .privacy-note {
        font-size: 0.75rem;
        color: #64748b;
        text-align: center;
        margin-top: 5px;
    }
    .stButton>button {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.1) 0%, rgba(79, 172, 254, 0.1) 100%) !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 242, 254, 0.4) !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #000000 !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.6) !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. إعداد مفتاح API الأمني
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("⚠️ لم يتم العثور على مفتاح Gemini API. يرجى إضافته في Streamlit Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# 4. اختيار اللغة بأسلوب آمن
with st
