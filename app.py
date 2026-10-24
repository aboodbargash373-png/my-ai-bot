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

# 2. تصميم الواجهة الاحترافي (Cyberpunk Dark Mode)
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #080a12 0%, #101426 50%, #05070b 100%);
        color: #e2e8f0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background: rgba(11, 15, 25, 0.95) !important;
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(0, 242, 254, 0.2);
    }
    .cyber-title {
        font-size: 2.5rem !important;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #00c6ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0, 242, 254, 0.4);
        margin-bottom: 2px;
    }
    .cyber-subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 25px;
        letter-spacing: 1.5px;
    }
    .metrics-container {
        display: flex;
        justify-content: space-around;
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(0, 242, 254, 0.3);
        border-radius: 14px;
        padding: 12px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .metric-value { color: #00f2fe; font-weight: bold; font-size: 0.9rem; text-align: center; }
    .metric-label { color: #64748b; font-size: 0.75rem; text-align: center; }
    .privacy-note {
        font-size: 0.75rem;
        color: #64748b;
        text-align: center;
        margin-top: 8px;
    }
    .stButton>button {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.12) 0%, rgba(79, 172, 254, 0.12) 100%) !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 242, 254, 0.4) !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #000000 !important;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.7) !important;
        border-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. إعداد مفتاح API
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("⚠️ لم يتم العثور على مفتاح Gemini API في Streamlit Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# 4. أداة تتبع الطلبات الفورية (AI Agent Tool)
def check_order_status(order_id: str) -> str:
    database = {
        "ORD-101": "طلبك قيد الشحن حالياً وسيصل خلال 48 ساعة 🚚",
        "ORD-202": "تم تجهيز الطلب وهو في انتظار شركة الشحن 📦",
        "ORD-303": "تم تسليم الطلب بنجاح. شكراً لتعاملكم معنا! ✅"
    }
    clean_id = order_id.strip().upper()
    if clean_id in database:
        return f"حالة الطلب {clean_id}: {database[clean_id]}"
    return f"عذراً، رقم الطلب {clean_id} غير موجود في النظام. يرجى التحقق من الرقم والمحاولة لاحقاً."

# 5. القائمة الجانبية وإعدادات اللغات
with st.sidebar:
    st.markdown("### ⚙️ Control Panel / التحكم")
    selected_language = st.selectbox(
        "🌐 Language / اللغة:",
        ["العربية 🇸🇦", "English 🇬🇧"],
        key="lang_select"
    )
    st.markdown("---")
    creativity_level = st.slider("⚡ Temperature / الابتكار:", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

is_arabic = "العربية" in selected_language

if is_arabic:
    full_instruction = """
    أنت "رداد" (Raddad Cyber AI)، نظام خدمة العملاء الأكثر تطوراً وذكاءً (AI Agent).
    مهمتك تقديم إجابات دقيقة، فائقة السرعة، واحترافية باللغة العربية حصراً وبإيجاز مفيد.
    """
    welcome_msg = "مرحباً بك في المستقبل! ⚡ أنا **رداد**. يمكنك التحدث معي، الاستعلام عن طلبياتك، أو إرسال صور وصوت مباشرة!"
    subtitle_text = "نظام الذكاء الاصطناعي التفاعلي متعدد الوسائط والخدمات"
    metric_vision = "وكيل ذكي (مباشر)"
    metric_latency = "زمن الاستجابة"
    metric_status = "نشط"
    shortcuts_title = "🚀 اختصارات سريعة للوكيل:"
    btn_s1 = "📦 تتبع ORD-101"
    btn_s2 = "📦 تتبع ORD-202"
    btn_s3 = "💡 الخدمات"
    btn_s4 = "🛠️ الدعم"
    tab_titles = ["📁 صورة", "📸 كاميرا", "🎙️ صوت"]
    privacy_msg = "🔒 البيانات المعالجة لا يتم حفظها على السيرفر لضمان الخصوصية والأمان التام."
    chat_placeholder = "اكتب استفسارك أو رقم الطلب (مثل ORD-101)..."
else:
    full_instruction = """
    You are "Raddad Cyber AI", an advanced, fast AI customer support agent (AI Agent).
    Provide accurate, lightning-fast, concise, and professional responses in English.
    """
    welcome_msg = "Welcome to the future! ⚡ I am **Raddad Cyber AI**. Ask me anything, track orders, or upload media!"
    subtitle_text = "Interactive Multimodal & Fast AI Agent System"
    metric_vision = "Fast AI Agent"
    metric_latency = "Latency"
    metric_status = "ONLINE"
    shortcuts_title = "🚀 Quick Agent Shortcuts:"
    btn_s1 = "📦 Track ORD-101"
    btn_s2 = "📦 Track ORD-202"
    btn_s3 = "💡 Services"
    btn_s4 = "🛠️ Support"
    tab_titles = ["📁 Image", "📸 Camera", "🎙️ Voice"]
    privacy_msg = "🔒 Processed data is not stored on the server to ensure absolute privacy."
    chat_placeholder = "Type your prompt or order ID (e.g. ORD-101)..."

if "current_lang" not in st.session_state or st.session_state.current_lang != selected_language:
    st.session_state.current_lang = selected_language
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
    st.session_state.last_response_time = "جاهز" if is_arabic else "Ready"

# 6. حالة المحرك في القائمة الجانبية
with st.sidebar:
    st.markdown("### 🤖 Engine Status / حالة المحرك")
    st.success("● Core Status: ACTIVE" if not is_arabic else "● حالة النواة: نشط")
    st.info("● Model: Gemini 3.8 Flash")
    st.info("● Mode: Streaming Fast Response")
    
    st.markdown("---")
    if st.button("🗑️ Reset Chat / إعادة ضبط", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
        st.session_state.last_response_time = "0.00"
        st.rerun()

# 7. تهيئة النموذج
model = genai.GenerativeModel(
    model_name="gemini-3.8-flash",
    system_instruction=full_instruction,
    generation_config={"temperature": creativity_level}
)

if "last_response_time" not in st.session_state:
    st.session_state.last_response_time = "جاهز" if is_arabic else "Ready"

# 8. العنوان والمؤشرات
st.markdown("<h1 class='cyber-title'>RADDAD CYBER AI</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='cyber-subtitle'>{subtitle_text}</div>", unsafe_allow_html=True)

latency_unit = "ثانية" if is_arabic else "s"
latency_val = st.session_state.last_response_time
latency_display = f"{latency_val} {latency_unit}" if latency_val not in ["جاهز", "Ready"] else latency_val

st.markdown(f"""
<div class="metrics-container">
    <div>
        <div class="metric-value">{metric_vision}</div>
        <div class="metric-label">{"نوع النظام" if is_arabic else "System Type"}</div>
    </div>
    <div>
        <div class="metric-value">{latency_display}</div>
        <div class="metric-label">{metric_latency}</div>
    </div>
    <div>
        <div class="metric-value">{metric_status}</div>
        <div class="metric-label">{"الحالة" if is_arabic else "Status"}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 9. عرض الرسائل
for msg in st.session_state.messages:
    avatar = "⚡" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# 10. الأزرار والاختصارات السريعة
st.markdown(f"##### {shortcuts_title}")
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

prompt_shortcut = None
with col1:
    if st.button(btn_s1, use_container_width=True):
        prompt_shortcut = "ما هي حالة الطلب رقم ORD-101؟" if is_arabic else "What is the status of order ORD-101?"
with col2:
    if st.button(btn_s2, use_container_width=True):
        prompt_shortcut = "أريد معرفة حالة طلبي ORD-202" if is_arabic else "I want to check order ORD-202"
with col3:
    if st.button(btn_s3, use_container_width=True):
        prompt_shortcut = "ما هي الخدمات والتسهيلات التي تقدمها؟" if is_arabic else "What services do you provide?"
with col4:
    if st.button(btn_s4, use_container_width=True):
        prompt_shortcut = "أحتاج لمساعدة في حل مشكلة تقنية." if is_arabic else "I need help with a technical issue."

# 11. تبويبات الوسائط المتعددة (صور / كاميرا / صوت)
st.markdown("---")
tab_upload, tab_camera, tab_audio = st.tabs(tab_titles)

image_object = None
audio_file_object = None

with tab_upload:
    uploaded_file = st.file_uploader("اختر صورة:" if is_arabic else "Select Image:", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image_object = Image.open(uploaded_file)
        st.image(image_object, caption="الصورة المرفوعة" if is_arabic else "Uploaded Image", use_container_width=True)

with tab_camera:
    camera_photo = st.camera_input("صورة بالكاميرا:" if is_arabic else "Camera Capture:")
    if camera_photo:
        image_object = Image.open(camera_photo)
        st.image(image_object, caption="اللقطة الحية" if is_arabic else "Captured Photo", use_container_width=True)

with tab_audio:
    audio_data = st.audio_input("تسجيل صوتي:" if is_arabic else "Record Voice:")
    if audio_data:
        audio_file_object = audio_data
        st.success("✅ تم تسجيل الصوت بنجاح!" if is_arabic else "✅ Audio recorded successfully!")

st.markdown(f"<div class='privacy-note'>{privacy_msg}</div>", unsafe_allow_html=True)

# 12. استقبال المعالجة والبث التدفقي المباشر (Streaming Response)
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
        start_time = time.time()
        
        # فحص سريع لطلبات الشحن
        tool_output = None
        if user_input:
            for code in ["ORD-101", "ORD-202", "ORD-303"]:
                if code in user_input.upper():
                    tool_output = check_order_status(code)
                    break
        
        content_payload = []
        if tool_output:
            prompt_final = f"نتيجة فحص نظام الطلبات: '{tool_output}'. صغ للعميل رداً مختصراً واحترافياً بنفس لغته."
            content_payload.append(prompt_final)
        else:
            if user_input:
                content_payload.append(user_input)
            else:
                default_prompt = "الرجاء الاستماع لهذه الرسالة الصوتية والإجابة عليها بشكل أسرع ولطيف:" if is_arabic else "Please listen to this audio message and respond:"
                content_payload.append(default_prompt)

        if image_object:
            content_payload.append(image_object)
        
        if audio_file_object:
            audio_bytes = audio_file_object.getvalue()
            content_payload.append({
                "mime_type": "audio/wav",
                "data": audio_bytes
            })

        try:
            # تفعيل البث المباشر (stream=True) لكتابة النص فوراً دون انتظار
            response_stream = model.generate_content(content_payload, stream=True)
            
            def stream_generator():
                for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text

            full_response = st.write_stream(stream_generator)

            elapsed_time = time.time() - start_time
            st.session_state.last_response_time = f"{elapsed_time:.2f}"
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            error_message = str(e)
            if "429" in error_message or "quota" in error_message.lower():
                st.warning("⚠️ عذراً، تم الوصول للحد الأقصى للتجارب المجانية اليومية." if is_arabic else "⚠️ Quota limit reached.")
            else:
                st.error(f"⚠️ حدث خطأ تقني: {error_message}")
