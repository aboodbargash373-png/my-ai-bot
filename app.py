import streamlit as st
import google.generativeai as genai
from PIL import Image

# إعدادات الصفحة
st.set_page_config(page_title="رداد - Raddad AI", page_icon="🤖", layout="centered")

# جلب مفتاح API من Secrets
API_KEY = st.secrets.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("⚠️ لم يتم العثور على مفتاح Gemini API. يرجى إضافته في Streamlit Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# إعداد التعليمات النظامية للتطوير
full_instruction = """
أنت "رداد"، مساعد خدمة العملاء الذكي.
مهمتك هي الإجابة عن استفسارات العملاء بأسلوب مهني، ودود، وسريع.
تحدث باللغة العربية دائماً وبلهجة جيدة ومحترمة.
"""

# شريط جانب التحكم بالحرارة
with st.sidebar:
    st.title("⚙️ الإعدادات")
    creativity_level = st.slider("مستوى الإبداع (Temperature):", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

# تهيئة الموديل (تحديث الاسم إلى gemini-3.8-flash)
model = genai.GenerativeModel(
    model_name="gemini-3.8-flash",
    system_instruction=full_instruction,
    generation_config={"temperature": creativity_level}
)

st.title("🤖 مساعد خدمة العملاء (رداد)")

# تهيئة رسائل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "مرحباً بك! ✋ أنا مساعد خدمة العملاء الذكي رداد. كيف يمكنني مساعدتك اليوم؟"}
    ]

# عرض المحادثة السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# رفع صور اختيارية
uploaded_file = st.file_uploader("إرفاق صورة (اختياري):", type=["jpg", "jpeg", "png"])
image_object = None
if uploaded_file:
    image_object = Image.open(uploaded_file)
    st.image(image_object, caption="الصورة المرفقة", use_container_width=True)

# استقبال المدخلات
user_input = st.chat_input("اكتب استفسارك هنا...")

if user_input:
    # إظهار رسالة المستخدم
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # توليد الإجابة
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

# زر مسح المحادثة بالجانب
with st.sidebar:
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "مرحباً بك! ✋ أنا مساعد خدمة العملاء الذكي رداد. كيف يمكنني مساعدتك اليوم؟"}
        ]
        st.rerun()
