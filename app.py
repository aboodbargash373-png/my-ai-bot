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

# 4. إدارة تغيير اللغة وإعادة ضبط الشات تلقائياً
with st.sidebar:
    st.markdown("### ⚙️ وحدة التحكم / Control Panel")
    
    # التقاط تغيير اللغة
    selected_language = st.selectbox(
        "🌐 لغة النظام / System Language:",
        ["العربية 🇸🇦", "English 🇬🇧"],
        key="lang_select"
    )
    st.markdown("---")
    creativity_level = st.slider("⚡ مستوى الابتكار (Temperature):", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

is_arabic = "العربية" in selected_language

# تحديد رسالة الترحيب والتعليمات حسب اللغة
if is_arabic:
    full_instruction = """
    أنت "رداد" (Raddad Cyber AI)، نظام خدمة العملاء الأكثر تطوراً وذكاءً.
    مهمتك تقديم إجابات دقيقة، فائقة السرعة، احترافية وبلهجة ودودة ومحترمة باللغة العربية حصراً.
    يمكنك تحليل الصوت، الصور المباشرة المأخوذة بالكاميرا، أو الملفات المرفقة والاستجابة لها بذكاء فائق.
    """
    welcome_msg = "مرحباً بك في المستقبل! ⚡ أنا **رداد**. يمكنك التحدث معي بالصوت، استخدام الكاميرا، أو كتابة استفسارك مباشرة!"
else:
    full_instruction = """
    You are "Raddad Cyber AI", an advanced, highly intelligent customer service agent.
    Your mission is to provide accurate, lightning-fast, and professional responses strictly in English.
    You can analyze live camera input, audio recordings, or uploaded media with high precision.
    """
    welcome_msg = "Welcome to the future! ⚡ I am **Raddad Cyber AI**. Feel free to speak, upload images, use your live camera, or type your query!"

# تحديث السجل إذا تغيرت اللغة
if "current_lang" not in st.session_state or st.session_state.current_lang != selected_language:
    st.session_state.current_lang = selected_language
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
    st.session_state.last_response_time = "جاهز" if is_arabic else "Ready"

# 5. الشريط الجانبي وتحديث حالة المحرك
with st.sidebar:
    st.markdown("### 🤖 حالة المحرك" if is_arabic else "### 🤖 Engine Status")
    st.success("● حالة النواة: نشط" if is_arabic else "● Core Status: ONLINE")
    st.info("● المحرك: Gemini 3.8 Flash" if is_arabic else "● Model: Gemini 3.8 Flash")
    st.info("● الميزات: كاميرا + صوت + نص" if is_arabic else "● Features: Vision + Audio + Text")
    
    st.markdown("---")
    if st.button("🗑️ إعادة ضبط الجلسة" if is_arabic else "🗑️ Reset Session", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
        st.session_state.last_response_time = "0.00"
        st.rerun()

# 6. تهيئة الموديل
model = genai.GenerativeModel(
    model_name="gemini-3.8-flash",
    system_instruction=full_instruction,
    generation_config={"temperature": creativity_level}
)

# 7. الهيدر وشريط المؤشرات الفعلي
st.markdown("<h1 class='cyber-title'>RADDAD CYBER AI</h1>", unsafe_allow_html=True)
subtitle_text = "نظام الذكاء الاصطناعي التفاعلي متعدد الوسائط واللغات" if is_arabic else "Interactive Multimodal & Multilingual AI Customer Support"
st.markdown(f"<div class='cyber-subtitle'>{subtitle_text}</div>", unsafe_allow_html=True)

latency_unit = "ثانية" if is_arabic else "s"
latency_val = st.session_state.last_response_time
latency_display = f"{latency_val} {latency_unit}" if latency_val not in ["جاهز", "Ready"] else latency_val

metric_vision = "صوت + رؤية مفعلة" if is_arabic else "Audio + Vision Active"
metric_latency = "زمن الاستجابة الفعلي" if is_arabic else "Real-time Latency"
metric_status = "نشط" if is_arabic else "ONLINE"

st.markdown(f"""
<div class="metrics-container">
    <div class="metric-card">
        <div class="metric-value">{metric_vision}</div>
        <div class="metric-label">{"المدخلات الذكية" if is_arabic else "Smart Inputs"}</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{latency_display}</div>
        <div class="metric-label">{metric_latency}</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{metric_status}</div>
        <div class="metric-label">{"حالة النظام" if is_arabic else "System Status"}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 8. عرض سجل المحادثة
for msg in st.session_state.messages:
    avatar = "⚡" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# 9. اختصارات سريعة
st.markdown("##### 🚀 اختصارات سريعة:" if is_arabic else "##### 🚀 Quick Shortcuts:")
col1, col2, col3, col4 = st.columns(4)

prompt_shortcut = None
with col1:
    btn_txt = "💡 الخدمات" if is_arabic else "💡 Services"
    if st.button(btn_txt, use_container_width=True):
        prompt_shortcut = "ما هي الخدمات والتسهيلات التي تقدمها؟" if is_arabic else "What services do you provide?"
with col2:
    btn_txt = "📦 الطلبات" if is_arabic else "📦 Orders"
    if st.button(btn_txt, use_container_width=True):
        prompt_shortcut = "كيف يمكنني تتبع حالة طلبي؟" if is_arabic else "How can I track my order?"
with col3:
    btn_txt = "🛠️ الدعم" if is_arabic else "🛠️ Support"
    if st.button(btn_txt, use_container_width=True):
        prompt_shortcut = "أحتاج لمساعدة في حل مشكلة تقنية." if is_arabic else "I need help with a technical issue."
with col4:
    btn_txt = "⚡ العروض" if is_arabic else "⚡ Offers"
    if st.button(btn_txt, use_container_width=True):
        prompt_shortcut = "ما هي أحدث العروض والخصومات المتاحة؟" if is_arabic else "What are the latest offers available?"

# 10. تبويبات الإدخال المتقدمة
st.markdown("---")
tab_titles = ["📁 رفع صورة", "📸 الكاميرا المباشرة", "🎙️ التسجيل الصوتي"] if is_arabic else ["📁 Upload Image", "📸 Live Camera", "🎙️ Voice Input"]
tab_upload, tab_camera, tab_audio = st.tabs(tab_titles)

image_object = None
audio_file_object = None

with tab_upload:
    uploaded_file = st.file_uploader("اختر صورة للتحليل:" if is_arabic else "Select an image for analysis:", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image_object = Image.open(uploaded_file)
        st.image(image_object, caption="الصورة المرفقة" if is_arabic else "Uploaded Image", use_container_width=True)

with tab_camera:
    camera_photo = st.camera_input("التقط صورة مباشرة لـ رداد:" if is_arabic else "Capture photo for Raddad:")
    if camera_photo:
        image_object = Image.open(camera_photo)
        st.image(image_object, caption="اللقطة الحية" if is_arabic else "Captured Photo", use_container_width=True)

with tab_audio:
    st.markdown("اضغط على زر التسجيل وتحدث بصوتك لـ رداد:" if is_arabic else "Press record and speak to Raddad:")
    audio_data = st.audio_input("تسجيل صوتي" if is_arabic else "Audio Recording")
    if audio_data:
        audio_file_object = audio_data
        st.success("✅ تم تسجيل الصوت بنجاح!" if is_arabic else "✅ Audio recorded successfully!")

privacy_msg = "🔒 الملفات والصور والتسجيلات الصوتية لا يتم حفظها لضمان الخصوصية." if is_arabic else "🔒 Uploaded files, images, and audio are processed privately and not stored."
st.markdown(f"<div class='privacy-note'>{privacy_msg}</div>", unsafe_allow_html=True)

# 11. استقبال المدخلات والتحليل
chat_placeholder = "اكتب استفسارك أو اطرح سؤالك الصوتي..." if is_arabic else "Type your prompt or audio question..."
user_input = st.chat_input(chat_placeholder)

if prompt_shortcut:
    user_input = prompt_shortcut

if user_input or audio_file_object:
    display_text = user_input if user_input else ("🎤 [رسالة صوتية مرسلة]" if is_arabic else "🎤 [Audio Message Sent]")
    
    with st.chat_message("user", avatar="👤"):
        st.write(display_text)
        if audio_file_object:
            st.audio(audio_file_object)
            
    st.session_state.messages.append({"role": "user", "content": display_text})

    with st.chat_message("assistant", avatar="⚡"):
        spinner_msg = "⚡ جاري المعالجة والتحليل..." if is_arabic else "⚡ Processing and analyzing data..."
        with st.spinner(spinner_msg):
            try:
                start_time = time.time()
                
                content_payload = []
                if user_input:
                    content_payload.append(user_input)
                else:
                    default_prompt = "الرجاء الاستماع لهذه الرسالة الصوتية والإجابة عليها بنفس اللغة وبأسلوب خدمة العملاء:" if is_arabic else "Please listen to this audio message and respond in the same language as an AI customer support agent:"
                    content_payload.append(default_prompt)

                if image_object:
                    content_payload.append(image_object)
                
                if audio_file_object:
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
                    st.warning("⚠️ عذراً، تم الوصول للحد الأقصى للتجارب المجانية اليومية. يرجى المحاولة لاحقاً!" if is_arabic else "⚠️ Quota limit reached. Please try again later!")
                else:
                    st.error(f"⚠️ حدث خطأ أثناء المعالجة: {error_message}")
