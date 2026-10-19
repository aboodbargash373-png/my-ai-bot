import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# إعداد الصفحة
st.set_page_config(page_title="شات بوت الشركات الذكي", page_icon="🤖")
st.title("🤖 أول بوت ذكي لخدمة العملاء")
st.write("ارفع ملف بيانات أو اكتب سؤالك لنرى كيف سيقوم البوت بالرد بدقة!")

# الشريط الجانبي للإعدادات
with st.sidebar:
    st.header("إعدادات البوت")
    # ضع مفتاحك هنا مباشرة لتجربته بسرعة، أو أدخله في المربع
    api_key = st.text_input("أدخل مفتاح Gemini API:", type="password")
    uploaded_file = st.file_uploader("ارفع ملف بيانات (اختياري - PDF):", type=["pdf"])

# قراءة الملف إذا تم رفعه
business_data = ""
if uploaded_file:
    reader = PdfReader(uploaded_file)
    for page in reader.pages:
        business_data += page.extract_text() or ""
    st.sidebar.success("تم قراءة الملف بنجاح!")

# سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# استقبال رسالة المستخدم
if prompt := st.chat_input("اكتب رسالتك هنا..."):
    if not api_key:
        st.error("الرجاء إدخال مفتاح Gemini API في الشريط الجانبي أولاً.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # إعداد الذكاء الاصطناعي
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.8-flash")

        system_prompt = f"""
        أنت مساعد ذكي لخدمة العملاء. أجب على الأسئلة بأسلوب لبق ومحترف باللغة العربية.
        معلومات الشركة المتاحة:
        {business_data if business_data else "لا توجد ملفات مرفقة، أجب بذكاء واقترح على المستخدم إدخال معلومات."}
        """

        full_query = f"{system_prompt}\n\nسؤال العميل: {prompt}"

        with st.chat_message("assistant"):
            with st.spinner("جاري الكتابة..."):
                response = model.generate_content(full_query)
                st.markdown(response.text)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})