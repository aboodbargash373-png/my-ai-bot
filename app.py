import streamlit as st
from google import genai

# 1. إعدادات الصفحة
st.set_page_config(page_title="Raddad Cyber AI", page_icon="⚡", layout="centered")

# 2. تعريف درجات الألوان للثيمات
THEMES = {
    "فستقي وأسود (الافتراضي)": {
        "bg": "#0d1117",
        "user_bubble": "#558b2f",
        "accent": "#558b2f"
    },
    "برغندي وأسود": {
        "bg": "#0d1117",
        "user_bubble": "#800020",
        "accent": "#800020"
    },
    "خمري وأسود": {
        "bg": "#0d1117",
        "user_bubble": "#7a1c2e",
        "accent": "#7a1c2e"
    }
}

# 3. اختيار الثيم من الشريط الجانبي
st.sidebar.title("إعدادات الثيم 🎨")
selected_theme = st.sidebar.selectbox(
    "اختر الثيم المفضّل:",
    list(THEMES.keys()),
    index=0
)

active_theme = THEMES[selected_theme]

# 4. تطبيق الـ CSS المخصص ديناميكياً لتحديث الألوان وتنسيق زر (+)
st.markdown(f"""
<style>
    /* خلفية التطبيق */
    .stApp {{
        background-color: {active_theme['bg']};
        color: #c9d1d9;
    }}
    
    /* العنوان الرئيسي */
    .cyber-title {{
        font-size: 2.2rem;
        font-weight: bold;
        text-align: center;
        color: {active_theme['accent']};
        margin-bottom: 25px;
    }}

    /* حاويات المحادثة */
    .chat-row-user {{
        display: flex;
        justify-content: flex-end;
        margin-bottom: 12px;
        width: 100%;
        direction: rtl;
    }}

    .chat-row-assistant {{
        display: flex;
        justify-content: flex-start;
        margin-bottom: 12px;
        width: 100%;
        direction: rtl;
    }}

    /* فقاعات الشات */
    .chat-bubble {{
        max-width: 75%;
        padding: 12px 16px;
        border-radius: 16px;
        font-size: 16px;
        line-height: 1.5;
        word-wrap: break-word;
    }}

    .user-bubble {{
        background-color: {active_theme['user_bubble']} !important;
        color: #ffffff;
        border-bottom-right-radius: 2px;
    }}

    .assistant-bubble {{
        background-color: #202c33;
        color: #ffffff;
        border-bottom-left-radius: 2px;
    }}

    /* جعل زر رفع الملفات يبدو ككبسة (+) بجانب خانة الإدخال */
    div[data-testid="stFileUploader"] {{
        padding: 0px !important;
        margin: 0px !important;
    }}
    
    div[data-testid="stFileUploader"] section {{
        padding: 6px 12px !important;
        border-radius: 10px !important;
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
        min-height: unset !important;
    }}

    div[data-testid="stFileUploader"] section span {{
        display: none !important;
    }}
</style>
""", unsafe_allow_html=True)

# 5. إعداد مفتاح API و Client
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("⚠️ يرجى إضافة GEMINI_API_KEY في Streamlit Secrets.")
    st.stop()

@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=API_KEY)

client = get_gemini_client()

SYSTEM_INSTRUCTION = "إذا لم تجد الجواب المناسب احكِي لا أعلم بأسلوب راقي ولا تؤلف نتائج من عندك، أنت 'رداد' مساعد خدمة عملاء ذكي وسريع جداً. أجب بإيجاز واحترافية باللغة العربية.,جاوب بلغت المستخدم الي سالك فيها"

# 6. الدوال الخاصة والـ RAG
def check_order_status(order_id: str) -> str:
    db = {
        "ORD-101": "طلبك قيد الشحن حالياً وسيصل خلال 48 ساعة 🚚",
        "ORD-202": "تم تجهيز الطلب وهو في انتظار شركة الشحن 📦",
        "ORD-303": "تم تسليم الطلب بنجاح ✅"
    }
    clean_id = order_id.strip().upper()
    return db.get(clean_id, f"رقم الطلب {clean_id} غير موجود في النظام.")

def check_developer_info(query: str) -> str:
    keywords = ["مين طورك", "فكرة مين", "صممك", "مطور", "من صنعك", "who made you", "طـورك"]
    if any(k in query.lower() for k in keywords):
        return "المطور الذي قام بتطوير رداد وصمم فكرته هو عبد الكريم (Abdulkareem)."
    return ""

def search_company_rag(query: str) -> str:
    knowledge_base = [
        "سياسة الإرجاع: يمكن إرجاع أي منتج خلال 14 يوم من تاريخ الشراء بشرط أن يكون بحالته الأصلية.",
        "أوقات العمل: دعم عملاء رداد يعمل على مدار الساعة 24/7 طوال أيام الأسبوع.",
        "طرق الدفع: ندعم الدفع الإلكتروني عبر البطاقات البنكية والدفع عند الاستلام."
    ]
    for doc in knowledge_base:
        if any(w in query.lower() for w in doc.lower().split() if len(w) > 3):
            return doc
    return ""

# تهيئة سياق الرسائل
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "مرحباً بك! ⚡ أنا **RADDAD**. كيف أستطيع مساعدتك اليوم؟"}]

# عرض العنوان الرئيسي
st.markdown("<h1 class='cyber-title'>RADDAD CYBER AI</h1>", unsafe_allow_html=True)

# عرض سجل الرسائل
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
            <div class="chat-row-user">
                <div class="chat-bubble user-bubble">
                    {msg["content"]}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="chat-row-assistant">
                <div class="chat-bubble assistant-bubble">
                    {msg["content"]}
                </div>
            </div>
        """, unsafe_allow_html=True)

# 7. شريط إدخال الرسائل والمرفقات (كبسة + بجانب صندوق الكتابة)
uploaded_file = st.file_uploader("➕ مرفق", type=None, label_visibility="collapsed", key="upload_file_plus")

user_input = st.chat_input("اكتب استفسارك أو رقم الطلب (مثل ORD-101)...")

# معالجة الإدخال
final_query = ""
if uploaded_file is not None:
    file_info = f"[تم إرفاق ملف: {uploaded_file.name}]"
    if user_input:
        final_query = f"{user_input} {file_info}"
    else:
        final_query = f"مرحباً رداد، قمت بإرفاق الملف التالي: {uploaded_file.name}"
elif user_input:
    final_query = user_input

if final_query:
    st.session_state.messages.append({"role": "user", "content": final_query})
    st.rerun()

# 8. توليد الرد بـ Gemini Stream (نفس الموديل gemini-3.6-flash)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_user_query = st.session_state.messages[-1]["content"]
    
    with st.chat_message("assistant", avatar="⚡"):
        extra_context = ""
        
        for code in ["ORD-101", "ORD-202", "ORD-303"]:
            if code in last_user_query.upper():
                extra_context = f"\n[نتيجة نظام الطلبات: {check_order_status(code)}]"
                break
        
        if not extra_context:
            dev_res = check_developer_info(last_user_query)
            if dev_res:
                extra_context = f"\n[معلومات المطور: {dev_res}]"

        if not extra_context:
            rag_res = search_company_rag(last_user_query)
            if rag_res:
                extra_context = f"\n[معلومات من دليل الشركة: {rag_res}]"

        prompt_final = last_user_query + extra_context if extra_context else last_user_query

        try:
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
            st.rerun()
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
