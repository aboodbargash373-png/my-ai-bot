import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="رداد - Raddad Cyber AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. حقن لغة التصميم المستقبلية (Futuristic Cyberpunk & Glassmorphism CSS)
st.markdown("""
<style>
    /* خلفية التطبيق المستقبلية */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #101426 0%, #080a12 100%);
        color: #e0e6ed;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* الشريط الجانبي الفاخر */
    section[data-testid="stSidebar"] {
        background: rgba(13, 17, 30, 0.85) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(0, 242, 254, 0.2);
    }

    /* العنوان الرئيسي وتأثير النيون */
    .cyber-title {
        font-size: 2.6rem !important;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #00c6ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 25px rgba(0, 242, 254, 0.4);
        margin-bottom: 5px;
    }
    
    .cyber-subtitle {
        text-align: center;
        color: #88a0c0;
        font-size: 0.95rem;
        margin-bottom: 25px;
        letter-spacing: 1px;
    }

    /* شريط المؤشرات الحي (Live Metrics Bar) */
    .metrics-container {
        display: flex;
        justify-content: space-around;
        background: rgba(16, 23, 42, 0.6);
        border: 1px solid rgba(0, 242, 254, 0.25);
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
    }
    .metric-card {
        text-align: center;
    }
    .metric-value {
        color: #00f2fe;
        font-weight: bold;
        font-size: 0.9rem;
    }
    .metric-label {
        color: #64748b;
        font-size: 0.75rem;
    }

    /* صندوق الرسائل */
    stChatMessage {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 12px !important;
        margin-bottom: 12px !important;
        backdrop-filter: blur(10px);
    }

    /* زريات الاختصارات السريعة */
    .stButton>button {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.1) 0%, rgba(79, 172, 254, 0.1) 100%) !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 242, 254, 0.4) !important;
        border-radius: 20px !important;
        transition: all 0.3s ease-in-out !important;
        font-weight: 600 !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #000000 !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.6) !important;
        transform: translateY(-2px);
    }

    /* مدخلات النصوص */
    .stChatInputContainer {
        border-radius: 25px !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.15) !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. إعداد مفتاح API
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("⚠️ لم يتم العثور على مفتاح Gemini API. يرجى إضافته في Streamlit Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# 4. التعليمات النظامية الذكية المتقدمة
full_instruction = """
أنت "رداد" (Raddad Cyber AI)، نظام خدمة العملاء الأكثر تطوراً وذكاءً.
مهمتك تقديم إجابات دقيقة، فائقة السرعة، احترافية وبلهجة ودودة ومحترمة باللغة العربية.
يمكنك الاستجابة للنصوص والصور وتحليل احتياجات العميل كخبير دعم فني ومبيعات ذكي.
"""

# 5. الشريط الجانبي (Sidebar & Configs)
with st.sidebar:
    st.markdown("### ⚙️ وحدة التحكم الفائقة")
    st.markdown("---")
    creativity_level = st.slider("⚡ مستوى الابتكار (Temperature):", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    
    st.markdown("---")
    st.markdown("### 🤖 حالة المحرك")
    st.success("● Core Status: ONLINE")
    st.info("● Model: Gemini 3.8 Flash")
    
    st.markdown("---")
    if st.button("🗑️ إعادة ضبط الجلسة", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "مرحباً بك في المستقبل! ⚡ أنا **رداد** - نظام خدمة العملاء الذكي. كيف يمكنني دعمك اليوم؟"}
        ]
        st.rerun()

# 6. تهيئة الموديل
model = genai.GenerativeModel(
    model_name="gemini-3.8-flash",
    system_instruction=full_instruction,
    generation_config={"temperature": creativity_level}
)

# 7. الهيدر والواجهة المستقبلية
st.markdown("<h1 class='cyber-title'>RADDAD CYBER AI</h1>", unsafe_allow_html=True)
st.markdown("<div class='cyber-subtitle'>نظام خدمة العملاء والذكاء الاصطناعي التفاعلي المتقدم</div>", unsafe_allow_html=True)

# شريط المؤشرات الحي (Metrics Bar)
st.markdown("""
<div class="metrics-container">
    <div class="metric-card">
        <div class="metric-value">99.9%</div>
        <div class="metric-label">دقة النظام</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">&lt; 0.4s</div>
        <div class="metric-label">زمن الاستجابة</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">ACTIVE</div>
        <div class="metric-label">الحالة</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 8. إدارة المحادثة والرسالة الترحيبية
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "مرحباً بك في المستقبل! ⚡ أنا **رداد** - نظام خدمة العملاء الذكي. كيف يمكنني دعمك اليوم؟"}
    ]

# عرض السجل السابق
for msg in st.session_state.messages:
    avatar = "⚡" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# 9. أزرار الأسئلة السريعة (Quick Action Chips)
st.markdown("##### 🚀 اختصارات سريعة:")
col1, col2, col3, col4 = st.columns(4)

prompt_shortcut = None
with col1:
    if st.button("💡 الخدمات", use_container_width=True):
        prompt_shortcut = "ما هي الخدمات والتسهيلات التي تقدمها؟"
with col2:
    if st.button("📦 الطلبات", use_container_width=True):
        prompt_shortcut = "كيف يمكنني تتبع حالة طلبي؟"
with col3:
    if st.button("🛠️ الدعم", use_container_width=True):
        prompt_shortcut = "أحتاج لمساعدة في حل مشكلة تقنية."
with col4:
    if st.button("⚡ العروض", use_container_width=True):
        prompt_shortcut = "ما هي أحدث العروض والخصومات المتاحة؟"

# 10. مرفق الصور الاختياري
uploaded_file = st.file_uploader("📷 إرفاق مستند أو صورة للتحليل الفوري:", type=["jpg", "jpeg", "png"])
image_object = None
if uploaded_file:
    image_object = Image.open(uploaded_file)
    st.image(image_object, caption="الورقة / الصورة المرفقة للتحليل", use_container_width=True)

# 11. استقبال المدخلات (سواء من الأزرار أو مربع الكتابة)
user_input = st.chat_input("اكتب استفسارك للذكاء الاصطناعي هنا...")

if prompt_shortcut:
    user_input = prompt_shortcut

if user_input:
    # عرض رسالة المستخدم
    with st.chat_message("user", avatar="👤"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # معالجة وتوليد الاستجابة
    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("⚡ جاري معالجة المعطيات عبر المحرك المتقدم..."):
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
                    st.error("⚠️ حدث خطأ غير متوقع أثناء المعالجة، يرجى المحاولة مرة أخرى.")
