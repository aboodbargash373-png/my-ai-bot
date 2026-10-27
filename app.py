import streamlit as st
from google import genai
import time

# 1. إعدادات الصفحة
st.set_page_config(page_title="رداد - Raddad Cyber AI", page_icon="⚡", layout="centered")

# 2. تصميم CSS خفيف ومباشر
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .cyber-title { font-size: 2.2rem; font-weight: bold; text-align: center; color: #58a6ff; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# 3. إعداد مفتاح API
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("⚠️ يرجى إضافة GEMINI_API_KEY في Streamlit Secrets.")
    st.stop()

# 4. تخزين اتصال الـ client في الذاكرة لمنع إعادة الاتصال الثقيل (السرعة)
@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=API_KEY)

client = get_gemini_client()
SYSTEM_INSTRUCTION = "ادا لم تجد الجواب المناسب احكي لا اعلم  ب اسلوب راقي ولا تؤلمف نتائج من عندك, أنت 'رداد' مساعد خدمة عملاء ذكي وسريع جداً. أجب بإيجاز واحترافية باللغة العربي."

# 5. أداة تتبع الطلبات المباشرة
def check_order_status(order_id: str) -> str:
    db = {
        "ORD-101": "طلبك قيد الشحن حالياً وسيصل خلال 48 ساعة 🚚",
        "ORD-202": "تم تجهيز الطلب وهو في انتظار شركة الشحن 📦",
        "ORD-303": "تم تسليم الطلب بنجاح ✅"
    }
    clean_id = order_id.strip().upper()
    return db.get(clean_id, f"رقم الطلب {clean_id} غير موجود في النظام.")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "مرحباً بك! ⚡ أنا **رداد**. كيف أستطيع مساعدتك اليوم؟"}]

st.markdown("<h1 class='cyber-title'>RADDAD CYBER AI</h1>", unsafe_allow_html=True)

# عرض سجل الرسائل
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
        # فحص محلي فوري للأداة
        tool_res = None
        for code in ["ORD-101", "ORD-202", "ORD-303"]:
            if code in user_input.upper():
                tool_res = check_order_status(code)
                break

        prompt_final = f"نتيجة فحص النظام لطلب العميل: {tool_res}" if tool_res else user_input

        try:
            # بث تدفقي سريع باستخدام المكتبة الجديدة والموديل المطلوب
            res_stream = client.models.generate_content_stream(
                model="gemini-3.6-flash",
                contents=prompt_final,
                config={"system_instruction": SYSTEM_INSTRUCTION}
            )
            
            def stream_gen():
                for chunk in res_stream:
                    if chunk.text:
                        yield chunk.text

            full_res = st.write_stream(stream_gen)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
