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

# 2. تصميم الواجهة (Cyberpunk CSS)
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
        font-size: 2.4rem !important;
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
    .metric-value { color: #00f2fe; font-weight: bold; font-size: 0.85rem; text-align: center; }
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

# 3. إعداد مفتاح API
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("⚠️ لم يتم العثور على مفتاح Gemini API. يرجى إضافته في Streamlit Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# 4. تعريف الأداة الحقيقية (Tool) لتتبع الطلبات
def track_order(order_id: str) -> str:
    """
    تتبع حالة الطلب بناءً على رقم الطلب المقدم من العميل.
    
    Args:
        order_id: رقم الطلب المراد الاستعلام عن حالته (مثل: ORD-101، ORD-202، ORD-303)
    """
    database = {
        "ORD-101": "طلبك قيد الشحن حالياً وسيصل خلال 48 ساعة 🚚",
        "ORD-202": "تم تجهيز الطلب وهو في انتظار الاستلام من قبل شركة الشحن 📦",
        "ORD-303": "تم تسليم الطلب بنجاح. شكراً لتعاملكم معنا! ✅"
    }
    
    clean_id = order_id.strip().upper()
    if clean_id in database:
        return f"حالة الطلب {clean_id}: {database[clean_id]}"
    else:
        return f"عذراً، رقم الطلب {clean_id} غير موجود في النظام. يرجى التحقق من الرقم والمحاولة لاحقاً."

# 5. إعدادات القائمة الجانبية واللغة
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
    أنت "رداد" (Raddad Cyber AI)، نظام خدمة العملاء الأذكى والأسرع.
    مهمتك تقديم إجابات فورية، دقيقة، واحترافية باللغة العربية حصراً.
    لديك القدرة على استخدام أدوات النظام (مثل تتبع الطلبات) فوراً عندما يطلب العميل ذلك، بالإضافة لتحليل الصور والصوت.
    """
    welcome_msg = "مرحباً بك في المستقبل! ⚡ أنا **رداد** (AI Agent). يمكنني مساعدتك في تتبع طلباتك، الإجابة عن استفساراتك، أو تحليل الصور والصوت فوراً!"
else:
    full_instruction = """
    You are "Raddad Cyber AI", an advanced, lightning-fast AI Agent for customer support.
    Your mission is to provide instant, accurate, and professional responses strictly in English.
    You have access to system tools (like order tracking) and multimodal capabilities.
    """
    welcome_msg = "Welcome to the future! ⚡ I am **Raddad Cyber AI** (AI Agent). I can help you track orders, answer questions, or process voice and images instantly!"

# تحديث السجل عند تغيير اللغة دون عمل مشاكل
if "current_lang" not in st.session_state or st.session_state.current_lang != selected_language:
    st.session_state.current_lang = selected_language
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
    st.session_state.last_response_time = "جاهز" if is_arabic else "Ready"

# 6. حالة المحرك
with st.sidebar:
    st.markdown("### 🤖 Engine Status / حالة المحرك")
    st.success("● Agent Status: ACTIVE" if not is_arabic else "● حالة الوكيل: نشط")
    st.info("● Model: Gemini 3.8 Flash + Tools")
    
    st.markdown("---")
    if st.button("🗑️ Reset / إعادة ضبط", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
        st.session_state.last_response_time = "0.00"
        st.rerun()

# 7. تهيئة نموذج الذكاء الاصطناعي مع ربط الأداة
model = genai.GenerativeModel(
    model_name="gemini-3.8-flash",
    system_instruction=full_instruction,
    tools=[track_order],
    generation_config={"temperature": creativity_level}
)

if "last_response_time" not in st.session_state:
    st.session_state.last_response_time = "جاهز" if is_arabic else "Ready"

# 8. العنوان والمؤشرات
st.markdown("<h1 class='cyber-title'>RADDAD CYBER AI</h1>", unsafe_allow_html=True)
subtitle_text = "وكيل الذكاء الاصطناعي التفاعلي المدعوم بالأدوات (AI Agent)" if is_arabic else "Interactive AI Agent Powered with System Tools"
st.markdown(f"<div class='cyber-subtitle'>{subtitle_text}</div>", unsafe_allow_html=True)

latency_unit = "ثانية" if is_arabic else "s"
latency_val = st.session_state.last_response_time
latency_display = f"{latency_val} {latency_unit}" if latency_val not in ["جاهز", "Ready"] else latency_val

metric_vision = "وكيل ذكي (Tools)" if is_arabic else "AI Agent (Tools)"
metric_latency = "سرعة الاستجابة" if is_arabic else "Latency"
metric_status = "نشط" if is_arabic else "ONLINE"

st.markdown(f"""
<div class="metrics-container">
    <div class="metric-card">
        <div class="metric-value">{metric_vision}</div>
        <div class="metric-label">{"نوع النظام" if is_arabic else "System Type"}</div>
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

# 9. عرض الرسائل بسلاسة دون رفع الشاشة
for msg in st.session_state.messages:
    avatar = "⚡" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# 10. الأزرار السريعة
st.markdown("##### 🚀 اختصارات سريعة (تجربة الوكيل):" if is_arabic else "##### 🚀 Quick Shortcuts (Agent Test):")
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

prompt_shortcut = None
with col1:
    btn_txt = "📦 تتبع ORD-101" if is_arabic else "📦 Track ORD-101"
    if st.button(btn_txt, use_container_width=True):
        prompt_shortcut = "ما هي حالة الطلب رقم ORD-101؟" if is_arabic else "What is the status of order ORD-101?"
with col2:
    btn_txt = "📦 تتبع ORD-202" if is_arabic else "📦 Track ORD-202"
    if st.button(btn_txt, use_container_width=True):
        prompt_shortcut = "أريد معرفة حالة طلبي ORD-202" if is_arabic else "I want to check order ORD-202"
with col3:
    btn_txt = "💡 الخدمات" if is_arabic else "💡 Services"
    if st.button(btn_txt, use_container_width=True):
        prompt_shortcut = "ما هي الخدمات والتسهيلات التي تقدمها؟" if is_arabic else "What services do you provide?"
with col4:
    btn_txt = "🛠️ الدعم" if is_arabic else "🛠️ Support"
    if st.button(btn_txt, use_container_width=True):
        prompt_shortcut = "أحتاج لمساعدة في حل مشكلة تقنية." if is_arabic else "I need help with a technical issue."

# 11. الوسائط (صورة / كاميرا / صوت)
st.markdown("---")
tab_titles = ["📁 صورة", "📸 كاميرا", "🎙️ صوت"] if is_arabic else ["📁 Image", "📸 Camera", "🎙️ Voice"]
tab_upload, tab_camera, tab_audio = st.tabs(tab_titles)

image_object = None
audio_file_object = None

with tab_upload:
    uploaded_file = st.file_uploader("اختر صورة:" if is_arabic else "Select Image:", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image_object = Image.open(uploaded_file)
        st.image(image_object, caption="الصورة" if is_arabic else "Uploaded Image", use_container_width=True)

with tab_camera:
    camera_photo = st.camera_input("صورة بالكاميرا:" if is_arabic else "Camera Capture:")
    if camera_photo:
        image_object = Image.open(camera_photo)
        st.image(image_object, caption="اللقطة الحية" if is_arabic else "Captured Photo", use_container_width=True)

with tab_audio:
    st.markdown("سجل صوتك:" if is_arabic else "Record Voice:")
    audio_data = st.audio_input("تسجيل صوتي" if is_arabic else "Audio Input")
    if audio_data:
        audio_file_object = audio_data
        st.success("✅ تم التسجيل!" if is_arabic else "✅ Recorded!")

privacy_msg = "🔒 البيانات المعالجة لا يتم حفظها على السيرفر لضمان الخصوصية." if is_arabic else "🔒 Uploaded data processed privately and not stored."
st.markdown(f"<div class='privacy-note'>{privacy_msg}</div>", unsafe_allow_html=True)

# 12. معالجة المدخلات بدون استدعاء st.rerun المزعج
chat_placeholder = "اكتب استفسارك أو رقم الطلب (مثل ORD-101)..." if is_arabic else "Type your prompt or order ID..."
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
        spinner_msg = "⚡ جاري الفحص والتنفيذ..." if is_arabic else "⚡ Processing..."
        with st.spinner(spinner_msg):
            try:
                start_time = time.time()
                
                content_payload = []
                if user_input:
                    content_payload.append(user_input)
                else:
                    default_prompt = "الرجاء الاستماع لهذه الرسالة الصوتية والإجابة عليها بنفس اللغة:" if is_arabic else "Please listen to this audio message and respond:"
                    content_payload.append(default_prompt)

                if image_object:
                    content_payload.append(image_object)
                
                if audio_file_object:
                    audio_bytes = audio_file_object.getvalue()
                    content_payload.append({
                        "mime_type": "audio/wav",
                        "data": audio_bytes
                    })

                # إنشاء شات مستمر وتنفيذ الأدوات تلقائياً بدون إعادة تحميل الصفحة
                chat = model.start_chat(enable_automatic_function_calling=True)
                response = chat.send_message(content_payload)

                elapsed_time = time.time() - start_time
                st.session_state.last_response_time = f"{elapsed_time:.2f}"

                bot_reply = response.text
                st.write(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                
                # تم حذف st.rerun() لمنع ارتفاع الشاشة للأعلى!

            except Exception as e:
                error_message = str(e)
                if "429" in error_message or "quota" in error_message.lower():
                    st.warning("⚠️ عذراً، تم الوصول للحد الأقصى للتجارب المجانية اليومية." if is_arabic else "⚠️ Quota limit reached.")
                else:
                    st.error(f"⚠️ حدث خطأ: {error_message}")
