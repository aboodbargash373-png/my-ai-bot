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

# 2. تصميم الواجهة السريعة (Cyberpunk CSS خفيف ونظيف)
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 50% 10%, #101426 0%, #080a12 100%);
        color: #e0e6ed;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background: rgba(13, 17, 30, 0.9) !important;
        backdrop-filter: blur(10px);
    }
    .cyber-title {
        font-size: 2.3rem !important;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .cyber-subtitle {
        text-align: center;
        color: #88a0c0;
        font-size: 0.9rem;
        margin-bottom: 20px;
    }
    .stButton>button {
        background: rgba(0, 242, 254, 0.1) !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        border-radius: 15px !important;
    }
    .stButton>button:hover {
        background: #00f2fe !important;
        color: #000 !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. إعداد مفتاح API
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("⚠️ مفتاح Gemini API غير مفقود في Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# 4. أداة تتبع الطلبات السريعة جداً
def check_order_status(order_id: str) -> str:
    database = {
        "ORD-101": "طلبك قيد الشحن حالياً وسيصل خلال 48 ساعة 🚚",
        "ORD-202": "تم تجهيز الطلب وهو في انتظار شركة الشحن 📦",
        "ORD-303": "تم تسليم الطلب بنجاح. شكراً لتعاملكم معنا! ✅"
    }
    clean_id = order_id.strip().upper()
    if clean_id in database:
        return f"حالة الطلب {clean_id}: {database[clean_id]}"
    return None

# 5. القائمة الجانبية البسيطة والسريعة
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    selected_language = st.selectbox("🌐 Language / اللغة:", ["العربية 🇸🇦", "English 🇬🇧"], key="lang_select")
    
    st.markdown("---")
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

is_arabic = "العربية" in selected_language

if is_arabic:
    system_prompt = "أنت 'رداد' (Raddad Cyber AI)، مساعد خدمة عملاء ذكي، ودود، فائق السرعة، وتجيب باللغة العربية حصراً."
    welcome_msg = "مرحباً بك! ⚡ أنا **رداد**. كيف يمكنني مساعدتك اليوم؟"
else:
    system_prompt = "You are 'Raddad Cyber AI', a fast and friendly customer service assistant. Answer strictly in English."
    welcome_msg = "Welcome! ⚡ I am **Raddad Cyber AI**. How can I help you today?"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]

# 6. تهيئة الموديل بأعلى سرعة خالية من التعقيد
model = genai.GenerativeModel(
    model_name="gemini-3.8-flash",
    system_instruction=system_prompt
)

# العناوين والواجهة
st.markdown("<h1 class='cyber-title'>RADDAD CYBER AI</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='cyber-subtitle'>{'وكيل خدمة العملاء الفائق السرعة' | is_arabic if is_arabic else 'Lightning-Fast AI Support Agent'}</div>", unsafe_allow_html=True)

# عرض الرسائل القديمة
for msg in st.session_state.messages:
    avatar = "⚡" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# إدخال المستخدم السريع
user_input = st.chat_input("اكتب رسالتك هنا... / Type your message...")

if user_input:
    with st.chat_message("user", avatar="👤"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("⚡ جاري الرد الفوري..."):
            try:
                # فحص سريع جداً للأداة إن وُجدت
                tool_output = None
                for code in ["ORD-101", "ORD-202", "ORD-303"]:
                    if code in user_input.upper():
                        tool_output = check_order_status(code)
                        break
                
                if tool_output:
                    final_prompt = f"نتيجة فحص النظام لطلب العميل: {tool_output}. قم بصياغة رد خدمة عملاء سريع واحترافي."
                else:
                    final_prompt = user_input

                response = model.generate_content(final_prompt)
                bot_reply = response.text
                
                st.write(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"⚠️ خطأ: {e}")
