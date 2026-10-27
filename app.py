import streamlit as st
from google import genai
from google.genai import types

# 1. إعدادات الصفحة والواجهة السيبرانية
st.set_page_config(page_title="رداد - Raddad Cyber AI", page_icon="⚡", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .cyber-title { font-size: 2.2rem; font-weight: bold; text-align: center; color: #58a6ff; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# 2. إعداد مفتاح API
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("⚠️ يرجى إضافة GEMINI_API_KEY في Streamlit Secrets.")
    st.stop()

@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=API_KEY)

client = get_gemini_client()

SYSTEM_INSTRUCTION = """إذا لم تجد الجواب المناسب احكي لا أعلم بأسلوب راقي ولا تؤلف نتائج من عندك. 
أنت 'رداد' مساعد خدمة عملاء ذكي وسريع جداً. استخدم الأدوات المتاحة (Tools أو RAG) بدقة للإجابة."""

# 3. الأدوات الحقيقية (Tools) + محرك الـ RAG
def check_order_status(order_id: str) -> str:
    """أداة حقيقية لفحص حالة الطلب في قاعدة البيانات."""
    db = {
        "ORD-101": "طلبك قيد الشحن حالياً وسيصل خلال 48 ساعة 🚚",
        "ORD-202": "تم تجهيز الطلب وهو في انتظار شركة الشحن 📦",
        "ORD-303": "تم تسليم الطلب بنجاح ✅"
    }
    clean_id = order_id.strip().upper()
    return db.get(clean_id, f"رقم الطلب {clean_id} غير موجود في النظام.")

def search_company_rag(query: str) -> str:
    """محرك RAG للبحث في سياسات الشركة الداخلية ودليل الخدمة."""
    knowledge_base = [
        "سياسة الإرجاع: يمكن إرجاع أي منتج خلال 14 يوم من تاريخ الشراء بشرط أن يكون بحالته الأصلية.",
        "أوقات العمل: دعم عملاء رداد يعمل على مدار الساعة 24/7 طوال أيام الأسبوع.",
        "طرق الدفع: ندعم الدفع الإلكتروني عبر البطاقات البنكية والدفع عند الاستلام."
    ]
    for doc in knowledge_base:
        if any(w in query.lower() for w in doc.lower().split() if len(w) > 3):
            return doc
    return "لا توجد معلومة مطابقة في دليل الشركة الداخلي."

tools_map = {
    "check_order_status": check_order_status,
    "search_company_rag": search_company_rag
}

config = types.GenerateContentConfig(
    tools=[check_order_status, search_company_rag],
    system_instruction=SYSTEM_INSTRUCTION
)

# 4. سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "مرحباً بك! ⚡ أنا **رداد**. كيف أستطيع مساعدتك اليوم؟"}]

st.markdown("<h1 class='cyber-title'>RADDAD CYBER AI</h1>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    avatar = "⚡" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

user_input = st.chat_input("اكتب استفسارك، رقم الطلب، أو ابحث في السياسات...")

if user_input:
    with st.chat_message("user", avatar="👤"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant", avatar="⚡"):
        try:
            # إرسال الرسالة للموديل مع إتاحة الأدوات (Tools & RAG)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_input,
                config=config
            )

            # إذا طلب الموديل استدعاء أداة حقيقية
            if response.function_calls:
                for call in response.function_calls:
                    tool_name = call.name
                    tool_args = call.args or {}
                    if tool_name in tools_map:
                        tool_result = tools_map[tool_name](**tool_args)
                        
                        # إرجاع نتيجة الأداة للموديل ليصيغها بجواب نهائي
                        final_prompt = f"سؤال المستخدم: {user_input}\nنتيجة فحص الأداة ({tool_name}): {tool_result}"
                        res_stream = client.models.generate_content_stream(
                            model="gemini-3.6-flash",
                            contents=final_prompt,
                            config={"system_instruction": SYSTEM_INSTRUCTION}
                        )
                        
                        def stream_tool_gen():
                            for chunk in res_stream:
                                if chunk.text:
                                    yield chunk.text

                        full_res = st.write_stream(stream_tool_gen)
                        st.session_state.messages.append({"role": "assistant", "content": full_res})
            else:
                # لو ما احتاج أدوات، بيجاوب مباشرة وبـ Streaming سريع مثل كودك الأصلي
                res_stream = client.models.generate_content_stream(
                    model="gemini-3.6-flash",
                    contents=user_input,
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
