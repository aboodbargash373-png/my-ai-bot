import streamlit as st
from google import genai

# 1. إعدادات الصفحة
st.set_page_config(page_title="Raddad Cyber AI", page_icon="⚡", layout="centered")

# 2. درجات ألوان الثيمات (تعرض بالألوان الدائرية الفخمة)
THEMES = {
    "🟢 ⬛ فستقي وأسود (الافتراضي)": {
        "accent": "#558b2f",
        "user_bg": "#558b2f",
        "bg_gradient": "linear-gradient(135deg, #0d1117 0%, #162214 100%)",
        "sidebar_bg": "#121a11",
        "preview": "🟢 ⬛"
    },
    "🔴 ⬛ برغندي وأسود": {
        "accent": "#a91d3a",
        "user_bg": "#800020",
        "bg_gradient": "linear-gradient(135deg, #0d1117 0%, #251015 100%)",
        "sidebar_bg": "#1a1012",
        "preview": "🔴 ⬛"
    },
    "🔵 ⚪ أزرق سماوي وأبيض": {
        "accent": "#00b4d8",
        "user_bg": "#0096c7",
        "bg_gradient": "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
        "sidebar_bg": "#0b1329",
        "preview": "🔵 ⚪"
    }
}

# اختيار الثيم من الـ Sidebar بشكل أنيق
st.sidebar.title("إعدادات الثيم 🎨")
selected_theme_name = st.sidebar.selectbox("اختر الثيم المفضّل:", list(THEMES.keys()), index=0, label_visibility="collapsed")
active_theme = THEMES[selected_theme_name]

# 3. حقن الـ CSS لتنسيق الواجهة بالكامل وتثبيت زر المشبك (📎) بجانب صندوق الكتابة بدقة
st.markdown(f"""
<style>
    /* خلفية التطبيق الشاملة */
    .stApp {{
        background: {active_theme['bg_gradient']};
        color: #c9d1d9;
    }}
    
    /* الشريط الجانبي */
    [data-testid="stSidebar"] {{
        background-color: {active_theme['sidebar_bg']};
    }}

    /* العنوان الرئيسي */
    .cyber-title {{
        font-size: 2.2rem;
        font-weight: bold;
        text-align: center;
        color: {active_theme['accent']};
        margin-bottom: 25px;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.05);
    }}

    /* حاويات المحادثة - يمين للمستخدم، يسار للبوت */
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

    /* فقاعات المحادثة */
    .chat-bubble {{
        max-width: 75%;
        padding: 12px 16px;
        border-radius: 18px;
        font-size: 16px;
        line-height: 1.5;
        word-wrap: break-word;
    }}

    /* فقاعة المستخدم بلون الثيم المختار */
    .user-bubble {{
        background-color: {active_theme['user_bg']} !important;
        color: #ffffff !important;
        border-bottom-right-radius: 4px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }}

    /* فقاعة البوت */
    .assistant-bubble {{
        background-color: #202c33 !important;
        color: #ffffff !important;
        border-bottom-left-radius: 4px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }}

    /* تنسيق زر رفع الملفات (المشبك 📎) ليصبح بجانب خانة الكتابة تماماً وبشكل دائري متناسق */
    div[data-testid="stChatInput"] {{
        bottom: 15px !important;
    }}

    div[data-testid="stFileUploader"] {{
        position: fixed;
        bottom: 21px;
        left: calc(50% - 310px); /* محاذاة زر المشبك بجانب صندوق الكتابة بدقة */
        z-index: 99999;
        width: 44px !important;
    }
    
    @media (max-width: 768px) {{
        div[data-testid="stFileUploader"] {{
            left: 15px;
        }}
    }}
    
    div[data-testid="stFileUploader"] section {{
        padding: 0px !important;
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
        min-height: 42px !important;
        background-color: #21262d !important;
        border: 1px solid {active_theme['accent']} !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }}
    
    div[data-testid="stFileUploader"] section span {{
        display: none !important;
    }}
    
    /* أيقونة المشبك (📎) بمنتصف الدائرة تماماً */
    div[data-testid="stFileUploader"] section::after {{
        content: "📎";
        font-size: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
    }}
</style>
""", unsafe_allow_html=True)

# 4. إعداد مفتاح API والـ Client
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("⚠️ يرجى إضافة GEMINI_API_KEY في Streamlit Secrets.")
    st.stop()

@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=API_KEY)

client = get_gemini_client()

SYSTEM_INSTRUCTION = "إذا لم تجد الجواب المناسب احكِي لا أعلم بأسلوب راقي ولا تؤلف نتائج من عندك، أنت 'رداد' مساعد خدمة عملاء ذكي وسريع جداً. أجب بإيجاز واحترافية باللغة العربية.,جاوب بلغت المستخدم الي سالك فيها"

# 5. الدوال الخاصة بالسيستم (RAG والطلبات)
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

# تهيئة الذاكرة
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "مرحباً بك! ⚡ أنا **RADDAD**. كيف أستطيع مساعدتك اليوم؟"}]

# عرض العنوان الرئيسي
st.markdown("<h1 class='cyber-title'>RADDAD CYBER AI</h1>", unsafe_allow_html=True)

# 6. عرض المحادثات بتنسيق الـ HTML المخصص (يمين للمستخدم ويسار للبوت)
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

# 7. واجهة الإدخال ورفع الملفات بالمشبك (📎) بجانب صندوق الكتابة
uploaded_file = st.file_uploader("", type=None, label_visibility="collapsed", key="file_plus_input")
user_input = st.chat_input("اكتب استفسارك أو رقم الطلب (مثل ORD-101)...")

# معالجة الإدخال
final_query = ""
if uploaded_file is not None:
    file_info = f"[تم إرفاق ملف/صورة: {uploaded_file.name}]"
    if user_input:
        final_query = f"{user_input} {file_info}"
    else:
        final_query = f"مرحباً رداد، قمت بإرفاق هذا الملف/الصورة: {uploaded_file.name}"
elif user_input:
    final_query = user_input

if final_query:
    st.session_state.messages.append({"role": "user", "content": final_query})
    st.rerun()

# 8. توليد الرد من Gemini (مع الحفاظ على الموديل gemini-3.6-flash)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_user_query = st.session_state.messages[-1]["content"]
    
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
        
        full_res = ""
        for chunk in res_stream:
            if chunk.text:
                full_res += chunk.text

        st.session_state.messages.append({"role": "assistant", "content": full_res})
        st.rerun()
    except Exception as e:
        st.error(f"حدث خطأ: {e}")
