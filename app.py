import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="رداد - Raddad Cyber AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. لغة التصميم المستقبلية (Cyberpunk CSS)
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 50% 10%, #101426 0%, #080a12 100%);
        color: #e0e6ed;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background: rgba(13, 17, 30, 0.85) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(0, 242, 254, 0.2);
    }
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
    .metrics-container {
        display: flex;
        justify-content: space-around;
        background: rgba(16, 23, 42, 0.6);
        border: 1px solid rgba(0, 242, 254, 0.25);
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 20px;
        backdrop-filter: blur(8px);
    }
    .metric-value { color: #00f2fe; font-weight: bold; font-size: 0.9rem; text-align: center; }
    .metric-label { color: #64748b; font-size: 0.75rem; text-align: center; }
    .privacy-note {
        font-size: 0.75rem;
        color: #64748b;
        text-align: center;
        margin-top: 5px;
    }
    .stButton>button {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.1) 0%, rgba(79, 172, 254, 0.1) 100%) !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 242, 254, 0.4) !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #000000 !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.6) !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. إعداد مفتاح API الأمني
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("⚠️ لم يتم العثور على مفتاح Gemini API. يرجى إضافته في Streamlit Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# 4. التعليمات النظامية
full_instruction = """
أنت "رداد" (Raddad Cyber AI)، نظام خدمة العملاء الأكثر تطوراً وذكاءً.
مهمتك تقديم إجابات دقيقة، فائقة السرعة، احترافية وبلهجة ودودة ومحترمة باللغة العربية.
يمكنك تحليل الصوت، الصور المباشرة المأخوذة بالكاميرا، أو الملفات المرفقة والاستجابة لها بذكاء فائق.
"""

# 5. الشريط الجانبي
with st.sidebar:
    st.markdown("### ⚙️ وحدة التحكم الفائقة")
    st.markdown("---")
    creativity_level = st.slider("⚡ مستوى الابتكار (Temperature):", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    
    st.markdown("---")
    st.markdown("### 🤖 حالة المحرك")
    st.success("● حالة النواة: نشط (ONLINE)")
    st.info("● المحرك: Gemini 3.8 Flash")
    st.info("● الميزات: كاميرا + صوت + نص مفعلة")
    
    st.markdown("---")
    if st.button("🗑️ إعادة ضبط الجلسة", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "مرحباً بك في المستقبل! ⚡ أنا **رداد** - نظام خدمة العملاء الذكي. كيف يمكنني دعمك اليوم؟"}
        ]
        st.session_state.last_response_time = "0.00"
        st.rerun()

# 6. تهيئة الموديل
model = genai.GenerativeModel(
    model_name="gemini-3.8-flash",
    system_instruction=full_instruction,
    generation_config={"temperature": creativity_level}
)

# 7. إدارة حالة زمن الاستجابة الفعلي
if "last_response_time" not in st.session_state:
    st.session_state.last_response_time = "جاهز"

# 8. الهيدر وشريط المؤشرات الفعلي
st.markdown("<h1 class='cyber-title'>RADDAD CYBER AI</h1>", unsafe_allow_html=True)
st.markdown("<div class='cyber-subtitle'>نظام الذكاء الاصطناعي التفاعلي متعدد الوسائط (صوت، صورة، نص)</div>", unsafe_allow_html=True)

latency_display = f"{st.session_state.last_response_time} ثانية" if st.session_state.last_response_time != "جاهز" else "جاهز"

st.markdown(f"""
<div class="metrics-container">
    <div class="metric-card">
        <div class="metric-value">صوت + رؤية مفعلة</div>
        <div class="metric-label">المدخلات الذكية</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{latency_display}</div>
        <div class="metric-label">زمن الاستجابة الفعلي</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">نشط</div>
        <div class="metric-label">حالة النظام</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 9. إدارة المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "مرحباً بك في المستقبل! ⚡ أنا **رداد**. يمكنك التحدث معي بالصوت، استخدام الكاميرا، أو كتابة استفسارك مباشرة!"}
    ]

for msg in st.session_state.messages:
    avatar = "⚡" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# 10. اختصارات سريعة
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

# 11. تبويبات الإدخال المتقدمة (صور، كاميرا، صوت/مايك)
st.markdown("---")
tab_upload, tab_camera, tab_audio = st.tabs(["📁 رفع ملف/صورة", "📸 التقاط بالكاميرا", "🎙️ تسجيل صوتي (ميكروفون)"])

image_object = None
audio_file_object = None

with tab_upload:
    uploaded_file = st.file_uploader("اختر صورة للتحليل:", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image_object = Image.open(uploaded_file)
        st.image(image_object, caption="الصورة المرفقة", use_container_width=True)

with tab_camera:
    camera_photo = st.camera_input("التقط صورة مباشرة لـ رداد:")
    if camera_photo:
        image_object = Image.open(camera_photo)
        st.image(image_object, caption="اللقطة الحية من الكاميرا", use_container_width=True)

with tab_audio:
    st.markdown("اضغط على زر التسجيل أدناه وتحدث بصوتك لـ رداد:")
    audio_data = st.audio_input("تسجيل صوتي مباشر")
    if audio_data:
        audio_file_object = audio_data
        st.success("✅ تم تسجيل الصوت بنجاح، اكتب سؤالك أو اضغط إرسال لمعالجة الصوت!")

st.markdown("<div class='privacy-note'>🔒 الملفات والصور والتسجيلات الصوتية المعالجة لا يتم حفظها على السيرفر لضمان خصوصيتك الكاملة.</div>", unsafe_allow_html=True)

# 12. استقبال المدخلات والتحليل (يدعم النص، الصورة، والصوت معاً)
user_input = st.chat_input("اكتب استفسارك أو اطرح سؤالك الصوتي...")

if prompt_shortcut:
    user_input = prompt_shortcut

# تفعيل الإرسال إذا وُجد نص، صورة، أو صوت
if user_input or audio_file_object:
    display_text = user_input if user_input else "🎤 [مستند صوتي مرسل للمساعد الذكي]"
    
    with st.chat_message("user", avatar="👤"):
        st.write(display_text)
        if audio_file_object:
            st.audio(audio_file_object)
            
    st.session_state.messages.append({"role": "user", "content": display_text})

    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("⚡ جاري معالجة الصوت والبيانات عبر المحرك المتقدم..."):
            try:
                start_time = time.time()
                
                # تجهيز محتوى الإرسال لـ Gemini
                content_payload = []
                if user_input:
                    content_payload.append(user_input)
                else:
                    content_payload.append("الرجاء الاستماع لهذه الرسالة الصوتية والإجابة عليها باللغة العربية بأسلوب خدمة العملاء:")

                if image_object:
                    content_payload.append(image_object)
                
                if audio_file_object:
                    # قراءة بيانات الصوت وإرسالها للموديل
                    audio_bytes = audio_file_object.getvalue()
                    content_payload.append({
                        "mime_type": "audio/wav",
                        "data": audio_bytes
                    })

                response = model.generate_content(content_payload)

                elapsed_time = time.time() - start_time
                st.session_state.last_response_time = f"{elapsed_time:.2f}"

                bot_reply = response.text
                st.write(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                st.rerun()

            except Exception as e:
                error_message = str(e)
                if "429" in error_message or "quota" in error_message.lower():
                    st.warning("⚠️ عذراً، النظام يشهد إقبالاً كبيراً حالياً وتم الوصول للحد الأقصى للتجارب المجانية اليومية. يرجى المحاولة لاحقاً!")
                else:
                    st.error(f"⚠️ حدث خطأ أثناء المعالجة: {error_message}")
