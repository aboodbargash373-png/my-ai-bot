import streamlit as st
import google.generativeai as genai
import time

# 1. إعدادات الصفحة
st.set_page_config(page_title="رداد - Raddad Cyber AI", page_icon="⚡", layout="centered")

# 2. تصميم سريع وبسيط
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .cyber-title { font-size: 2rem; font-weight: bold; text-align: center; color: #58a6ff; }
</style>
""", unsafe_allow_html=True)

# 3. إعداد المفتاح
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("⚠️ يرجى إضافة GEMINI_API_KEY في Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# 4. أداة تتبع الطلبات
def check_order_status(order_id: str) -> str:
    db = {
        "ORD-101": "طلبك قيد الشحن حالياً وسيصل خلال 48 ساعة 🚚",
        "ORD-202": "تم تجهيز الطلب وهو في انتظار شركة الشحن 📦",
        "ORD-303": "تم تسليم الطلب بنجاح ✅"
    }
    clean_id = order_id.strip().upper()
    return db.get(clean_id, f"رقم الطلب {clean_id} غير موجود.")

# 5. تهيئة الموديل الخفيف
model = genai.GenerativeModel(
    model_name="gemini-3.8-flash",
    system_instruction="أنت 'رداد' مساعد خدمة عملاء ذكي وسريع جداً. أجب بأسلوب مختصر واحترافي."
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "مرحباً بك! ⚡ أنا **رداد**. كيف أستطيع مساعدتك اليوم؟"}]

st.markdown("<h1 class='cyber-title'>RADDAD CYBER AI</h1>", unsafe_allow_html=True)

# عرض المحادثة
for msg in st.session_state.messages:
    avatar = "⚡" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

user_input = st.chat_input("اكتب استفسارك أو رقم الطلب (مثل ORD-101)...")

if user_input:
    with st.chat_message("user", avatar="👤"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant", avatar="⚡"):
        # فحص سريع جداً للأداة محلياً قبل الاتصال بـ Gemini
        tool_res = None
        for code in ["ORD-101", "ORD-202", "ORD-303"]:
            if code in user_input.upper():
                tool_res = check_order_status(code)
                break

        prompt_to_send = f"نتيجة النظام للطلب: {tool_res}" if tool_res else user_input

        try:
            # استخدام البث المباشر المباشر لتسريع ظهور أول كلمة
            res_stream = model.generate_content(prompt_to_send, stream=True)
            
            def stream_gen():
                for chunk in res_stream:
                    if chunk.text:
                        yield chunk.text

            full_res = st.write_stream(stream_gen)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
        except Exception as e:
            st.error(f"خطأ: {e}")
