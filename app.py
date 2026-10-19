import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import datetime

# 1. إعدادات الصفحة والواجهة
st.set_page_config(
    page_title="Smart Enterprise AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

# 2. إعداد مفتاح API الأمان عبر Streamlit Secrets أو شريط الجانب
api_key = st.secrets.get("GEMINI_API_KEY", None)

with st.sidebar:
    st.title("⚙️ الإعدادات والمستندات")
    
    if not api_key:
        api_key = st.text_input("أدخل مفتاح Gemini API الخاص بك:", type="password")
        if not api_key:
            st.warning("⚠️ يرجى إدخال مفتاح GEMINI_API_KEY للاستمرار.")
            st.stop()
    else:
        st.success("🔒 تم تفعيل مفتاح API بنجاح!")
    
    st.markdown("---")
    st.subheader("📄 رفع قاعدة المعرفة (PDF)")
    uploaded_files = st.file_uploader(
        "ارفع ملفات PDF الخاصة بشركتك (كتالوجات، أسئلة شائعة، سياسات):",
        type=["pdf"],
        accept_multiple_files=True
    )
    
    # استخراج النصوص من ملفات الـ PDF المرفوعة
    pdf_text = ""
    if uploaded_files:
        with st.spinner("جاري قراءة وتحليل ملفات الـ PDF..."):
            for uploaded_file in uploaded_files:
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        pdf_text += extracted + "\n"
        st.success(f"✅ تم تحميل {len(uploaded_files)} ملف(ات) بنجاح!")

    st.markdown("---")
    st.subheader("🛠️ أدوات المحادثة")
    
    # زر إعادة ضبط المحادثة
    if st.button("🗑️ مسح المحادثة والبدء من جديد", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # زر الدعم البشري
    st.markdown("---")
    st.subheader("📞 الدعم الفني")
    st.markdown("[💬 تواصل مع الدعم البشري عبر واتساب](https://wa.me/0789944348)")

# 3. إعداد نموذج Gemini
genai.configure(api_key=api_key)

# توجيه النظام (System Prompt) لضمان إجابات احترافية
system_instruction = f"""
أنت ممثل خدمة عملاء محترف وذكي جداً يعمل لدى شركة.
وظيفتك الأساسية هي الإجابة على استفسارات العملاء بدقة وسرعة وأسلوب مهذب ولطيف.

قاعدة المعرفة المتاحة لديك من ملفات الشركة هي:
---
{pdf_text if pdf_text else "لم يتم رفع ملفات PDF بعد. أجب بشكل عام ووجه العميل لرفع مستندات الشركة للحصول على تفاصيل أدق."}
---

قواعد العمل:
1. التزم بالمعلومات المذكورة في قاعدة المعرفة المرفقة أعلاه قدر الإمكان.
2. إذا لم تجد الإجابة في المستندات، أجب بأسلوب راقٍ واقترح على العميل التواصل مع الدعم البشري.
3. أجب بنفس اللغة التي يتحدث بها العميل (عربي / إنجليزي).
"""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=system_instruction
)

# 4. إدارة سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "مرحباً بك! 👋 أنا مساعدك الذكي لخدمة العملاء. كيف يمكنني مساعدتك اليوم؟"}
    ]

st.title("🤖 Smart Enterprise Customer Support AI")
st.caption("مساعد الذكاء الاصطناعي التفاعلي المعتمد على مستندات الشركة وقواعد المعرفة")

# عرض المحادثات السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 5. استقبال مدخلات المستخدم
if user_input := st.chat_input("اكتب استفسارك هنا..."):
    # إضافة سؤال المستخدم
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # توليد الإجابة
    with st.chat_message("assistant"):
        with st.spinner("جاري التفكير والأجابة..."):
            try:
                # تحضير تاريخ المحادثة للنموذج
                chat_history = []
                for msg in st.session_state.messages[:-1]:
                    role = "user" if msg["role"] == "user" else "model"
                    chat_history.append({"role": role, "parts": [msg["content"]]})
                
                chat = model.start_chat(history=chat_history)
                response = chat.send_message(user_input)
                
                bot_reply = response.text
                st.write(bot_reply)
                
                # حفظ رد البوت
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {str(e)}")

# 6. زر تصدير المحادثة في الشريط الجانبي
with st.sidebar:
    if len(st.session_state.messages) > 1:
        st.markdown("---")
        chat_log = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        st.download_button(
            label="📥 تحميل سجل المحادثة (TXT)",
            data=chat_log,
            file_name=f"chat_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
