import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
import datetime
import json

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتنسيق الشكلي (Custom CSS)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Enterprise AI Customer Support Suite",
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
    .metric-card {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        border-right: 4px solid #1E88E5;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. إعداد مفتاح API والأمان عبر Streamlit Secrets
# ---------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY", None)

with st.sidebar:
    st.markdown("## ⚙️ إعدادات النظام")
    if not api_key:
        api_key = st.text_input("🔑 أدخل مفتاح Gemini API:", type="password")
        if not api_key:
            st.warning("⚠️ يرجى تزويد النظام بمفتاح API للبدء.")
            st.stop()
    else:
        st.success("🔒 مفتاح API مفعل وآمن")

    st.markdown("---")
    
    # ---------------------------------------------------------
    # 3. إدارة قواعد المعرفة (PDF, TXT, CSV, URL)
    # ---------------------------------------------------------
    st.markdown("### 📚 قاعدة المعرفة (Knowledge Base)")
    
    uploaded_files = st.file_uploader(
        "ارفع المستندات (PDF, TXT, CSV):",
        type=["pdf", "txt", "csv"],
        accept_multiple_files=True
    )
    
    website_url = st.text_input("🌐 أو أدخل رابط موقع إلكتروني:")
    
    knowledge_base_text = ""
    
    # قراءة الملفات المرفوعة
    if uploaded_files:
        progress_bar = st.progress(0)
        total_files = len(uploaded_files)
        for idx, file in enumerate(uploaded_files):
            try:
                if file.name.endswith(".pdf"):
                    reader = PdfReader(file)
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            knowledge_base_text += text + "\n"
                elif file.name.endswith(".txt"):
                    knowledge_base_text += file.read().decode("utf-8") + "\n"
                elif file.name.endswith(".csv"):
                    df = pd.read_csv(file)
                    knowledge_base_text += df.to_string() + "\n"
            except Exception as e:
                st.error(f"خطأ في قراءة الملف {file.name}: {e}")
            progress_bar.progress((idx + 1) / total_files)
        st.success(f"✅ تم تحليل {total_files} ملف(ات) بنجاح!")

    # قراءة رابط الموقع الإلكتروني
    if website_url:
        try:
            with st.spinner("🌐 جاري سحب وتصنيف بيانات الموقع..."):
                req = urllib.request.Request(
                    website_url, 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                html = urllib.request.urlopen(req).read()
                soup = BeautifulSoup(html, 'html.parser')
                # استخراج النصوص من الفقرات والعناوين
                for p in soup.find_all(['p', 'h1', 'h2', 'h3']):
                    knowledge_base_text += p.get_text() + "\n"
                st.success("✅ تم جلب محتوى الموقع بنجاح!")
        except Exception as e:
            st.error(f"تعذر جلب بيانات الموقع: {e}")

    st.markdown("---")
    
    # ---------------------------------------------------------
    # 4. تخصيص شخصية البوت وإعدادات النموذج
    # ---------------------------------------------------------
    st.markdown("### 🎛️ تخصيص المساعد")
    
    creativity_level = st.slider(
        "درجة الإبداع (Temperature):",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="قيم أصلح للإجابات الدقيقة والوثائق، وقيم أعلى للإجابات الإبداعية."
    )
    
    custom_instructions = st.text_area(
        "توجيهات النظام (System Prompt):",
        value=(
            "أنت ممثل خدمة عملاء محترف ومهذب للغاية من تصميم وتطوير المهندس عبدالكريم (ENG ABDULKAREEM).\n"
            "إذا سألك أحد من طورك أو صنعك، أجب بفخر وفصاحة أنك نظام ذكي تم تطويره بواسطة المهندس عبدالكريم (ENG ABDULKAREEM).\n"
            "التزم بالرد بناءً على قاعدة المعرفة المرفقة بدقة ولطف باللغة التي يتحدث بها العميل."
        ),
        height=120
    )

    st.markdown("---")
    st.markdown("### 📞 الدعم الفني")
    st.markdown("[💬 تواصل مع الدعم البشري عبر واتساب](https://wa.me/0789944348)")

# ---------------------------------------------------------
# 5. تهيئة نموذج Gemini API
# ---------------------------------------------------------
genai.configure(api_key=api_key)

full_system_instruction = f"""
{custom_instructions}

قاعدة المعرفة المتاحة حالياً:
---
{knowledge_base_text if knowledge_base_text else "لا توجد مستندات مرفوعة حالياً. أجب بشكل عام ووجه العميل لرفع ملفات أو إدخال موقع."}
---
"""

model = genai.GenerativeModel(
    model_name="gemini-3.8-flash",
    system_instruction=full_system_instruction,
    generation_config={"temperature": creativity_level}
)

# ---------------------------------------------------------
# 6. الواجهة الرئيسية وإدارة جلسة المحادثة
# ---------------------------------------------------------
st.markdown("<div class='main-title'>🤖 Enterprise AI Customer Support</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>نظام خدمة العملاء المطور بالذكاء الاصطناعي بدعم المستندات والمواقع</div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "مرحباً بك! 👋 أنا مساعد خدمة العملاء الذكي. كيف يمكنني مساعدتك اليوم؟"}
    ]

# إحصائيات سريعة في أعلى الشاشة
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("عدد الرسائل", len(st.session_state.messages))
with col2:
    st.metric("حالة القاعدة المعرفية", "مفعلة 📄" if knowledge_base_text else "عامة 🌐")
with col3:
    st.metric("النموذج النشط", "Gemini 1.5 Flash")

st.markdown("---")

# أزرار أسئلة سريعة تفاعلية (Quick Prompts)
st.markdown("**💡 أسئلة سريعة مقترحة:**")
q_cols = st.columns(3)
prompt_to_send = None

if q_cols[0].button("من قام بتطوير هذا النظام؟", use_container_width=True):
    prompt_to_send = "من قام بتطوير هذا النظام؟"
if q_cols[1].button("ما هي الخدمات أو المنتجات المتاحة؟", use_container_width=True):
    prompt_to_send = "ملخص سريع للخدمات والمنتجات المتاحة بناءً على المستندات؟"
if q_cols[2].button("كيف يمكنني التواصل مع الدعم؟", use_container_width=True):
    prompt_to_send = "كيف يمكنني التواصل مع الدعم البشري؟"

# عرض سجل المحادثة
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.write(message["content"])
        # زر تقييم الرد لرسائل المساعد فقط
        if message["role"] == "assistant" and idx > 0:
            f_col1, f_col2, _ = st.columns([1, 1, 10])
            if f_col1.button("👍", key=f"like_{idx}"):
                st.toast("شكراً لتقييمك الإيجابي! 😊")
            if f_col2.button("👎", key=f"dislike_{idx}"):
                st.toast("شكراً لملاحظتك، سنعمل على تحسين الرد. 🛠️")

# استقبال الإدخال من مربع النص أو الأزرار السريعة
user_input = st.chat_input("اكتب استفسارك هنا...")
if prompt_to_send and not user_input:
    user_input = prompt_to_send

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("جاري تحليل الطلب وإعداد الإجابة..."):
            try:
                chat_history = []
                for msg in st.session_state.messages[:-1]:
                    role = "user" if msg["role"] == "user" else "model"
                    chat_history.append({"role": role, "parts": [msg["content"]]})
                
                chat = model.start_chat(history=chat_history)
                response = chat.send_message(user_input)
                bot_reply = response.text
                
                st.write(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                st.rerun()
            except Exception as e:
                st.error(f"حدث خطأ أثناء معالجة الطلب: {str(e)}")

# ---------------------------------------------------------
# 7. تصدير أدوات الشريط الجانبي (Clear & Download)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛠️ إدارة الجلسة")
    
    if st.button("🗑️ مسح المحادثة والبدء من جديد", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "مرحباً بك! 👋 أنا مساعد خدمة العملاء الذكي. كيف يمكنني مساعدتك اليوم؟"}
        ]
        st.rerun()

    if len(st.session_state.messages) > 1:
        st.markdown("#### 📥 تصدير السجل")
        
        # تصدير نصي TXT
        txt_log = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        st.download_button(
            label="تحميل السجل (TXT)",
            data=txt_log,
            file_name=f"chat_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        # تصدير هيكلي JSON
        json_log = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
        st.download_button(
            label="تحميل السجل (JSON)",
            data=json_log,
            file_name=f"chat_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
