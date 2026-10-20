import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import pandas as pd
from PIL import Image
import urllib.request
from bs4 import BeautifulSoup
import datetime
import json

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتنسيق الشكلي (Custom CSS)
# ---------------------------------------------------------
st.set_page_config(
    page_title="RADDAD AI",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1rem;
        color: #666;
        margin-bottom: 20px;
    }
    .stButton>button {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. إعداد مفتاح API والأمان عبر Streamlit Secrets
# ---------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY", None)

if not api_key:
    with st.sidebar:
        api_key = st.text_input("🔑 أدخل مفتاح Gemini API:", type="password")
        if not api_key:
            st.warning("⚠️ يرجى تزويد النظام بمفتاح API للبدء.")
            st.stop()

genai.configure(api_key=api_key)

# ---------------------------------------------------------
# 3. الشريط الجانبي
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ التحكم بالجلسة")
    
    creativity_level = st.slider(
        "درجة الإبداع (Temperature):",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1
    )
    
    website_url = st.text_input("🌐 أدخل رابط موقع للتحليل:")
    
    st.markdown("---")
    st.markdown("### 📞 الدعم الفني")
    st.markdown("[💬 تواصل مع الدعم البشري عبر واتساب](https://wa.me/0789944348)")

# توجيهات النظام مخفية داخل الكود لحمايتها
HIDDEN_SYSTEM_PROMPT = (
    "أنت ممثل خدمة عملاء محترف ومهذب للغاية من تصميم وتطوير المهندس عبدالكريم (ENG ABDULKAREEM).\n"
    "إذا سألك أحد من طورك أو صنعك، أجب بفخر وفصاحة أنك نظام ذكي تم تطويره بواسطة المهندس عبدالكريم (ENG ABDULKAREEM).\n"
    "التزم بالرد بناءً على المستندات والملفات المرفقة بدقة ولطف باللغة التي يتحدث بها العميل."
    
)

# ---------------------------------------------------------
# 4. الواجهة الرئيسية
# ---------------------------------------------------------
st.markdown("<div class='main-title'>🤖 RADDAD AI </div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>نظام خدمة العملاء المطور بالذكاء الاصطناعي</div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": " RADDAD AI مرحباً بك! 👋 أنا مساعد خدمة العملاء الذكي. كيف يمكنني مساعدتك اليوم؟"}
    ]

# أزرار أسئلة سريعة
st.markdown("**💡 أسئلة سريعة مقترحة:**")
q_cols = st.columns(3)
prompt_to_send = None

if q_cols[0].button("من قام بتطوير هذا النظام؟", use_container_width=True):
    prompt_to_send = "من قام بتطوير هذا النظام؟"
if q_cols[1].button("ملخص الخدمات المتاحة؟", use_container_width=True):
    prompt_to_send = "ما هي الخدمات أو المنتجات المتاحة بناءً على الملفات والموقع؟"
if q_cols[2].button("التواصل مع الدعم", use_container_width=True):
    prompt_to_send = "كيف يمكنني التواصل مع الدعم البشري؟"

# عرض سجل المحادثة
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "image" in message:
            st.image(message["image"], width=250)
        if message["role"] == "assistant" and idx > 0:
            f_col1, f_col2, _ = st.columns([1, 1, 10])
            if f_col1.button("👍", key=f"like_{idx}"):
                st.toast("شكراً لتقييمك الإيجابي! 😊")
            if f_col2.button("👎", key=f"dislike_{idx}"):
                st.toast("شكراً لملاحظتك! 🛠️")

# ---------------------------------------------------------
# 5. منطقة الإرفاق والكتابة المتكاملة بجانب بعضها
# ---------------------------------------------------------
st.markdown("---")

# تصميم صف أفقي يضم زر الإرفاق بجانب صندوق الكتابة أو فوقه مباشرة بشكل مدمج
col_upload, col_input = st.columns([1, 4])

with col_upload:
    uploaded_file = st.file_uploader(
        "➕ إرفاق ملف/صورة",
        type=["pdf", "txt", "csv", "png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )

user_input = st.chat_input("اكتب استفسارك هنا...")
if prompt_to_send and not user_input:
    user_input = prompt_to_send

if user_input:
    extracted_text = ""
    image_object = None

    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".pdf"):
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text: extracted_text += text + "\n"
            elif uploaded_file.name.endswith(".txt"):
                extracted_text += uploaded_file.read().decode("utf-8") + "\n"
            elif uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
                extracted_text += df.to_string() + "\n"
            elif uploaded_file.type.startswith("image"):
                image_object = Image.open(uploaded_file)
        except Exception as e:
            st.error(f"خطأ في قراءة المرفق: {e}")

    # معالجة رابط الموقع إن وجد
    if website_url:
        try:
            req = urllib.request.Request(website_url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req).read()
            soup = BeautifulSoup(html, 'html.parser')
            for p in soup.find_all(['p', 'h1', 'h2', 'h3']):
                extracted_text += p.get_text() + "\n"
        except Exception as e:
            pass

    # تجهيز رسالة المستخدم
    msg_data = {"role": "user", "content": user_input}
    if image_object:
        msg_data["image"] = image_object
    st.session_state.messages.append(msg_data)

    # إعداد النموذج وإرسال الطلب
    full_instruction = f"{HIDDEN_SYSTEM_PROMPT}\n\nالمعرفة المرفقة:\n{extracted_text}"
    model = genai.GenerativeModel(
        model_name="gemini-3.8-flash",
        system_instruction=full_instruction,
        generation_config={"temperature": creativity_level}
    )

    with st.chat_message("assistant"):
        with st.spinner("جاري تحليل المعطيات والإجابة..."):
            try:
                if image_object:
                    response = model.generate_content([user_input, image_object])
                else:
                    response = model.generate_content(user_input)
                
                bot_reply = response.text
                st.write(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                st.rerun()
                    except Exception as e:
            error_message = str(e)
            if "429" in error_message or "quota" in error_message.lower():
                st.warning("⚠️ عذراً، النظام يشهد إقبالاً كبيراً حالياً وتم الوصول للحد الأقصى للتجارب المجانية اليومية. يرجى المحاولة لاحقاً!")
            else:
                st.error("⚠️ حدث خطأ غير متوقع، يرجى المحاولة مرة أخرى.")

# إدارة الجلسة في أسفل الشريط الجانبي
with st.sidebar:
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = [
             {"role": "assistant", "content": "مرحباً بك! 🤚 أنا مساعد خدمة العملاء الذكي 'رداد'. كيف يمكنني مساعدتك اليوم؟"}

        ]
        st.rerun()
