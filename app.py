import os
import io
import json
import time
import uuid
import html
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from PIL import Image

# =====================================================

# 1. إعدادات التطبيق

# =====================================================

st.set_page_config(
page_title="RADDAD CYBER AI",
page_icon="⚡",
layout="wide",
initial_sidebar_state="expanded"
)

MODEL_NAME = "gemini-3.8-flash"
MAX_HISTORY = 20

# =====================================================

# 2. النصوص متعددة اللغات

# =====================================================

TEXT = {
"العربية": {
"subtitle": "وكيلك الذكي — أسرع، أذكى، وأسهل",
"settings": "⚙️ الإعدادات",
"language": "🌐 اللغة",
"theme": "🎨 المظهر",
"dark": "داكن",
"light": "فاتح",
"creativity": "مستوى الإبداع",
"engine": "🤖 حالة المحرك",
"online": "متصل بالإعدادات",
"new_chat": "➕ محادثة جديدة",
"export": "📥 تصدير المحادثة",
"reset": "🗑️ مسح المحادثة",
"shortcuts": "⚡ اختصارات سريعة",
"track1": "📦 تتبع ORD-101",
"track2": "📦 تتبع ORD-202",
"services": "💡 الخدمات",
"support": "🛠️ الدعم الفني",
"upload": "📁 الملفات",
"camera": "📸 الكاميرا",
"voice": "🎙️ الصوت",
"choose_file": "اختر صورة أو ملف PDF أو ملف صوتي",
"camera_text": "التقط صورة",
"record": "سجّل رسالتك الصوتية",
"chat_placeholder": "اكتب رسالتك هنا...",
"welcome": "أهلًا! أنا رداد ⚡ كيف بقدر أساعدك اليوم؟",
"thinking": "⚡ رداد يفكر...",
"error_key": "مفتاح Gemini API غير موجود. أضفه في Secrets.",
"error_model": "تعذر الاتصال بـ Gemini. تحقق من المفتاح وسجلات التطبيق.",
"status": "جاهز",
"latency": "زمن الرد",
"assistant": "رداد",
"user": "أنت",
"read": "🔊 اقرأ آخر رد",
"copy_note": "يمكنك نسخ الرد من قائمة الرسالة.",
"download": "تنزيل المحادثة",
"privacy": "🔒 لا يحفظ هذا الإصدار المحادثات في قاعدة بيانات خارجية.",
"services_answer": "الخدمات المتاحة:\n• المساعدة والإجابة عن الأسئلة\n• تحليل الصور والملفات المدعومة\n• الاستعلام التجريبي عن الطلبات\n• إنشاء تذاكر دعم تجريبية",
"ticket": "تم إنشاء تذكرة دعم تجريبية:",
"not_found": "رقم الطلب غير موجود في بيانات الطلبات التجريبية.",
"invalid_file": "تعذر قراءة الملف:",
"empty": "اكتب رسالة أو أرفق ملفًا ثم أرسل الطلب.",
"send": "إرسال",
},
"English": {
"subtitle": "Your intelligent assistant — faster, smarter, simpler",
"settings": "⚙️ Settings",
"language": "🌐 Language",
"theme": "🎨 Appearance",
"dark": "Dark",
"light": "Light",
"creativity": "Creativity",
"engine": "🤖 Engine status",
"online": "Configuration loaded",
"new_chat": "➕ New chat",
"export": "📥 Export conversation",
"reset": "🗑️ Clear conversation",
"shortcuts": "⚡ Quick actions",
"track1": "📦 Track ORD-101",
"track2": "📦 Track ORD-202",
"services": "💡 Services",
"support": "🛠️ Support",
"upload": "📁 Files",
"camera": "📸 Camera",
"voice": "🎙️ Voice",
"choose_file": "Choose an image, PDF, or audio file",
"camera_text": "Take a picture",
"record": "Record your voice message",
"chat_placeholder": "Type your message here...",
"welcome": "Welcome! I'm Raddad ⚡ How can I help you today?",
"thinking": "⚡ Raddad is thinking...",
"error_key": "Gemini API key is missing. Add it to Secrets.",
"error_model": "Could not connect to Gemini. Check your key and app logs.",
"status": "Ready",
"latency": "Response time",
"assistant": "Raddad",
"user": "You",
"read": "🔊 Read latest response",
"copy_note": "You can copy a response from its message menu.",
"download": "Download conversation",
"privacy": "🔒 This version does not save conversations to an external database.",
"services_answer": "Available services:\n• General assistance and questions\n• Supported image and file analysis\n• Demo order tracking\n• Demo support tickets",
"ticket": "Demo support ticket created:",
"not_found": "That order ID was not found in the demo order data.",
"invalid_file": "Could not read file:",
"empty": "Write a message or attach a file before sending.",
"send": "Send",
},
}

# =====================================================

# 3. إعداد الحالة

# =====================================================

if "language" not in st.session_state:
st.session_state.language = "العربية"

if "theme" not in st.session_state:
st.session_state.theme = "Dark"

if "messages" not in st.session_state:
st.session_state.messages = []

if "last_answer" not in st.session_state:
st.session_state.last_answer = ""

if "last_latency" not in st.session_state:
st.session_state.last_latency = None

if "pending_prompt" not in st.session_state:
st.session_state.pending_prompt = ""

if "uploaded_version" not in st.session_state:
st.session_state.uploaded_version = 0

if "request_id" not in st.session_state:
st.session_state.request_id = 0

# =====================================================

# 4. الألوان والتصميم

# =====================================================

dark_mode = st.session_state.theme == "Dark"

if dark_mode:
BG = "#07111F"
PANEL = "#0D1B2D"
CARD = "#10243A"
TEXT_COLOR = "#E5EDF7"
MUTED = "#9BAFC7"
BORDER = "#203A57"
ACCENT = "#45B8FF"
INPUT_BG = "#0D1B2D"
else:
BG = "#F2F6FC"
PANEL = "#FFFFFF"
CARD = "#E8F1FC"
TEXT_COLOR = "#15243A"
MUTED = "#526780"
BORDER = "#D2DFEF"
ACCENT = "#087BC1"
INPUT_BG = "#FFFFFF"

direction = "rtl" if st.session_state.language == "العربية" else "ltr"
alignment = "right" if direction == "rtl" else "left"

st.markdown(
f""" <style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

```
:root {{
    color-scheme: {"dark" if dark_mode else "light"};
}}

html, body, [class*="css"] {{
    font-family: 'Cairo', sans-serif;
}}

.stApp {{
    background: {BG};
    color: {TEXT_COLOR};
}}

[data-testid="stHeader"] {{
    background: transparent;
}}

.block-container {{
    max-width: 1250px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}}

section[data-testid="stSidebar"] {{
    background: {PANEL};
    border-right: 1px solid {BORDER};
}}

.hero {{
    padding: 30px 25px;
    border-radius: 24px;
    border: 1px solid {BORDER};
    background: linear-gradient(135deg, {PANEL}, {CARD});
    margin-bottom: 20px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.08);
    direction: {direction};
    text-align: {alignment};
}}

.hero h1 {{
    color: {ACCENT};
    font-size: clamp(26px, 4vw, 42px);
    font-weight: 800;
    margin: 0;
    letter-spacing: 0.5px;
}}

.hero p {{
    color: {MUTED};
    font-size: 15px;
    margin-top: 10px;
    margin-bottom: 0;
}}

.badge {{
    display: inline-block;
    padding: 5px 12px;
    border: 1px solid {BORDER};
    border-radius: 50px;
    color: {ACCENT};
    font-size: 12px;
    margin-top: 15px;
}}

.metric {{
    background: {PANEL};
    border: 1px solid {BORDER};
    padding: 15px;
    border-radius: 16px;
    text-align: center;
    min-height: 85px;
}}

.metric-value {{
    color: {ACCENT};
    font-size: 19px;
    font-weight: 800;
}}

.metric-label {{
    color: {MUTED};
    font-size: 12px;
    margin-top: 4px;
}}

div[data-testid="stChatMessage"] {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 12px;
    margin-bottom: 12px;
}}

.stButton button {{
    border-radius: 12px;
    border: 1px solid {BORDER};
    min-height: 42px;
    transition: all 0.2s ease;
}}

.stButton button:hover {{
    border-color: {ACCENT};
    color: {ACCENT};
}}

div[data-testid="stChatInput"] {{
    border-color: {BORDER};
}}

.note {{
    text-align: center;
    font-size: 12px;
    color: {MUTED};
    padding: 12px 0;
}}

[data-testid="stMarkdownContainer"] {{
    color: {TEXT_COLOR};
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
}}

.stTabs [data-baseweb="tab"] {{
    border-radius: 10px;
    padding: 10px 14px;
}}
</style>
""",
unsafe_allow_html=True
```

)

# =====================================================

# 5. مفتاح API والاتصال

# =====================================================

api_key = os.getenv("GEMINI_API_KEY", "")

try:
if not api_key:
api_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
pass

@st.cache_resource(show_spinner=False)
def get_client(key):
return genai.Client(api_key=key)

# =====================================================

# 6. أدوات الوكيل الذكي

# =====================================================

def check_order_status(order_id):
database = {
"ORD-101": "طلبك قيد الشحن حاليًا، والموعد التجريبي المتوقع خلال 48 ساعة.",
"ORD-202": "تم تجهيز الطلب وهو بانتظار شركة الشحن.",
"ORD-303": "تم تسليم الطلب بنجاح.",
}

```
order_id = order_id.strip().upper()

if order_id in database:
    return f"{order_id}: {database[order_id]}"

return None
```

def create_demo_ticket(issue):
ticket_id = "RAD-" + uuid.uuid4().hex[:8].upper()

```
return (
    f"رقم التذكرة: {ticket_id}\n"
    f"المشكلة: {issue}\n"
    f"وقت الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    "هذه تذكرة تجريبية غير محفوظة في قاعدة بيانات."
)
```

def detect_quick_action(prompt, language):
upper_prompt = prompt.upper()

```
for order_id in ("ORD-101", "ORD-202", "ORD-303"):
    if order_id in upper_prompt:
        result = check_order_status(order_id)
        if result:
            return result

lower_prompt = prompt.lower()

service_words = [
    "الخدمات", "خدماتكم", "شو بتقدم", "ماذا تقدم",
    "services", "what can you do", "available services"
]

if any(word in lower_prompt for word in service_words):
    return TEXT[language]["services_answer"]

return None
```

# =====================================================

# 7. تعليمات المساعد

# =====================================================

def get_system_instruction(language):
if language == "العربية":
return """
أنت رداد RADDAD CYBER AI، مساعد ذكي احترافي.

التعليمات:

* أجب باللغة العربية ما لم يطلب المستخدم لغة أخرى.
* كن دقيقًا ومباشرًا ومفيدًا.
* لا تخترع معلومات أو نتائج أو عمليات لم تنفذها.
* عند تحليل صورة أو ملف، اعتمد على المحتوى الذي وصل إليك فقط.
* إذا كانت المعلومات غير كافية، اسأل سؤالًا واضحًا.
* لا تدّع أنك متصل بقاعدة بيانات أو موقع خارجي إذا لم تكن كذلك.
* بيانات الطلبات وتذاكر الدعم في هذا التطبيق تجريبية.
* اجعل الردود العادية مختصرة، واستخدم التفصيل عندما يطلب المستخدم ذلك.
  """
  return """
  You are RADDAD CYBER AI, a professional intelligent assistant.

Instructions:

* Respond in English unless the user requests another language.
* Be accurate, direct, and helpful.
* Never invent facts or claim an action was completed when it was not.
* Analyze uploaded media only using the content provided.
* Ask a clear question when important information is missing.
* Never claim to be connected to a database or external system when you are not.
* Order data and support tickets in this app are demos.
* Keep ordinary answers concise and expand when requested.
  """

# =====================================================

# 8. الشريط الجانبي

# =====================================================

with st.sidebar:
st.markdown("## ⚡ RADDAD")
st.caption("CYBER AI • SMART AGENT")

```
st.divider()

st.markdown("### " + TEXT[st.session_state.language]["settings"])

language_options = ["العربية", "English"]
selected_language = st.selectbox(
    TEXT[st.session_state.language]["language"],
    language_options,
    index=language_options.index(st.session_state.language),
    key="language_control"
)

if selected_language != st.session_state.language:
    st.session_state.language = selected_language
    st.rerun()

language = st.session_state.language
t = TEXT[language]

theme_options = ["Dark", "Light"]
theme_labels = {
    "Dark": t["dark"],
    "Light": t["light"],
}

selected_theme = st.selectbox(
    t["theme"],
    theme_options,
    index=theme_options.index(st.session_state.theme),
    format_func=lambda value: theme_labels[value],
    key="theme_control"
)

if selected_theme != st.session_state.theme:
    st.session_state.theme = selected_theme
    st.rerun()

creativity = st.slider(
    t["creativity"],
    min_value=0.0,
    max_value=1.0,
    value=0.3,
    step=0.1
)

st.divider()

st.markdown("### " + t["engine"])
st.success("● Gemini API" if api_key else "● API key missing")
st.info("Model: " + MODEL_NAME)

if st.session_state.last_latency is not None:
    st.metric(
        t["latency"],
        f"{st.session_state.last_latency:.2f} s"
    )

st.divider()

if st.button(t["new_chat"], use_container_width=True):
    st.session_state.messages = []
    st.session_state.last_answer = ""
    st.session_state.last_latency = None
    st.session_state.pending_prompt = ""
    st.session_state.uploaded_version += 1
    st.rerun()

if st.button(t["reset"], use_container_width=True):
    st.session_state.messages = []
    st.session_state.last_answer = ""
    st.session_state.pending_prompt = ""
    st.rerun()

if st.session_state.messages:
    export_text = "\n\n".join(
        f"{m['role'].upper()}:\n{m['content']}"
        for m in st.session_state.messages
    )

    st.download_button(
        t["export"],
        data=export_text,
        file_name="raddad_conversation.txt",
        mime="text/plain",
        use_container_width=True
    )
```

# =====================================================

# 9. العنوان والإحصائيات

# =====================================================

language = st.session_state.language
t = TEXT[language]

subtitle = t["subtitle"]

st.markdown(
f""" <div class="hero"> <h1>⚡ RADDAD CYBER AI</h1> <p>{html.escape(subtitle)}</p> <span class="badge">● {MODEL_NAME}</span> </div>
""",
unsafe_allow_html=True
)

m1, m2, m3 = st.columns(3)

with m1:
st.markdown(
f""" <div class="metric"> <div class="metric-value">AI</div> <div class="metric-label">SMART AGENT</div> </div>
""",
unsafe_allow_html=True
)

with m2:
latency = (
f"{st.session_state.last_latency:.2f} s"
if st.session_state.last_latency is not None
else t["status"]
)

```
st.markdown(
    f"""
    <div class="metric">
        <div class="metric-value">{html.escape(latency)}</div>
        <div class="metric-label">{t["latency"]}</div>
    </div>
    """,
    unsafe_allow_html=True
)
```

with m3:
status_text = "READY" if api_key else "API KEY NEEDED"

```
st.markdown(
    f"""
    <div class="metric">
        <div class="metric-value">{status_text}</div>
        <div class="metric-label">SYSTEM STATUS</div>
    </div>
    """,
    unsafe_allow_html=True
)
```

# =====================================================

# 10. الأزرار السريعة

# =====================================================

st.markdown("### " + t["shortcuts"])

col1, col2, col3, col4 = st.columns(4)

if language == "العربية":
shortcut_prompts = [
"ما حالة الطلب ORD-101؟",
"ما حالة الطلب ORD-202؟",
"ما الخدمات التي تقدمها؟",
"أحتاج إلى مساعدة في مشكلة تقنية.",
]
else:
shortcut_prompts = [
"What is the status of order ORD-101?",
"What is the status of order ORD-202?",
"What services do you provide?",
"I need help with a technical issue.",
]

shortcut_columns = [col1, col2, col3, col4]
shortcut_labels = [
t["track1"],
t["track2"],
t["services"],
t["support"],
]

for index, column in enumerate(shortcut_columns):
with column:
if st.button(
shortcut_labels[index],
use_container_width=True,
key=f"shortcut_{index}"
):
st.session_state.pending_prompt = shortcut_prompts[index]
st.rerun()

# =====================================================

# 11. عرض المحادثة

# =====================================================

if not st.session_state.messages:
st.info(t["welcome"])

for index, message in enumerate(st.session_state.messages):
role = message["role"]
avatar = "⚡" if role == "assistant" else "👤"

```
with st.chat_message(role, avatar=avatar):
    st.markdown(message["content"])

    if role == "assistant" and message["content"]:
        if st.button(
            "🔊 " + ("استمع للرد" if language == "العربية" else "Read aloud"),
            key=f"speak_{index}"
        ):
            speech_text = json.dumps(
                message["content"],
                ensure_ascii=False
            )

            speech_lang = "ar" if language == "العربية" else "en"

            components.html(
                f"""
                <script>
                const text = {speech_text};
                const language = "{speech_lang}";
                if ("speechSynthesis" in window) {{
                    window.speechSynthesis.cancel();
                    const utterance = new SpeechSynthesisUtterance(text);
                    utterance.lang = language;
                    utterance.rate = 1.0;
                    window.speechSynthesis.speak(utterance);
                }}
                </script>
                """,
                height=0
            )
```

# =====================================================

# 12. الوسائط المتعددة

# =====================================================

st.divider()

tab_file, tab_camera, tab_voice = st.tabs([
t["upload"],
t["camera"],
t["voice"]
])

uploaded_files = []
camera_photo = None
audio_data = None

with tab_file:
uploaded_files = st.file_uploader(
t["choose_file"],
type=[
"png", "jpg", "jpeg", "webp",
"pdf",
"mp3", "wav", "m4a", "ogg", "aac", "flac"
],
accept_multiple_files=True,
key=f"upload_{st.session_state.uploaded_version}"
)

```
if uploaded_files:
    for uploaded in uploaded_files:
        st.caption(f"📎 {uploaded.name}")

        if uploaded.type.startswith("image/"):
            st.image(
                uploaded,
                caption=uploaded.name,
                use_container_width=True
            )
```

with tab_camera:
camera_photo = st.camera_input(
t["camera_text"],
key=f"camera_{st.session_state.uploaded_version}"
)

with tab_voice:
audio_data = st.audio_input(
t["record"],
key=f"audio_{st.session_state.uploaded_version}"
)

```
if audio_data:
    st.audio(audio_data)
```

# =====================================================

# 13. استقبال الرسائل

# =====================================================

chat_placeholder = t["chat_placeholder"]

typed_prompt = st.chat_input(chat_placeholder)

if typed_prompt:
st.session_state.pending_prompt = typed_prompt

prompt = st.session_state.pending_prompt

if prompt or uploaded_files or camera_photo or audio_data:

```
if not prompt:
    prompt = (
        "حلل الملفات المرفقة وأخبرني بمحتواها."
        if language == "العربية"
        else "Analyze the attached files and describe their content."
    )

st.session_state.pending_prompt = ""

user_message = prompt

if audio_data:
    user_message += (
        "\n[تم إرفاق تسجيل صوتي]"
        if language == "العربية"
        else "\n[Audio recording attached]"
    )

st.session_state.messages.append({
    "role": "user",
    "content": user_message
})

with st.chat_message("user", avatar="👤"):
    st.markdown(prompt)

    if uploaded_files:
        for file in uploaded_files:
            st.caption("📎 " + file.name)

    if camera_photo:
        st.image(camera_photo, width=250)

    if audio_data:
        st.audio(audio_data)

# -------------------------------------------------
# معالجة الأدوات المحلية دون استدعاء النموذج
# -------------------------------------------------

quick_result = detect_quick_action(prompt, language)

if quick_result:
    answer = quick_result

    with st.chat_message("assistant", avatar="⚡"):
        st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    st.session_state.last_answer = answer

    st.session_state.uploaded_version += 1
    st.rerun()

# -------------------------------------------------
# الاتصال بالنموذج
# -------------------------------------------------

if not api_key:
    st.error(t["error_key"])
    st.stop()

start_time = time.perf_counter()

try:
    client = get_client(api_key)

    # تجهيز تاريخ مختصر لتقليل حجم الطلب
    history = st.session_state.messages[:-1][-MAX_HISTORY:]

    contents = []

    for item in history:
        role = "model" if item["role"] == "assistant" else "user"

        contents.append(
            types.Content(
                role=role,
                parts=[
                    types.Part.from_text(text=item["content"])
                ]
            )
        )

    current_parts = [
        types.Part.from_text(text=prompt)
    ]

    # ملفات الصور وPDF والصوت
    if uploaded_files:
        for uploaded in uploaded_files:
            mime_type = uploaded.type

            supported = (
                mime_type.startswith("image/")
                or mime_type.startswith("audio/")
                or mime_type == "application/pdf"
            )

            if not supported:
                st.warning(
                    t["invalid_file"] + " " + uploaded.name
                )
                continue

            current_parts.append(
                types.Part.from_bytes(
                    data=uploaded.getvalue(),
                    mime_type=mime_type
                )
            )

    # صورة الكاميرا
    if camera_photo:
        current_parts.append(
            types.Part.from_bytes(
                data=camera_photo.getvalue(),
                mime_type="image/jpeg"
            )
        )

    # التسجيل الصوتي
    if audio_data:
        audio_mime = audio_data.type or "audio/wav"

        current_parts.append(
            types.Part.from_bytes(
                data=audio_data.getvalue(),
                mime_type=audio_mime
            )
        )

    contents.append(
        types.Content(
            role="user",
            parts=current_parts
        )
    )

    config = types.GenerateContentConfig(
        system_instruction=get_system_instruction(language),
        temperature=creativity,
        max_output_tokens=2048,
        thinking_config=types.ThinkingConfig(
            thinking_level="low"
        )
    )

    with st.chat_message("assistant", avatar="⚡"):
        response_placeholder = st.empty()
        streamed_text = ""

        with st.spinner(t["thinking"]):
            for chunk in client.models.generate_content_stream(
                model=MODEL_NAME,
                contents=contents,
                config=config
            ):
                chunk_text = chunk.text

                if chunk_text:
                    streamed_text += chunk_text
                    response_placeholder.markdown(
                        streamed_text + " ▌"
                    )

        answer = streamed_text.strip()

        if not answer:
            answer = (
                "لم يصل رد نصي من النموذج. جرّب مرة ثانية."
                if language == "العربية"
                else "The model returned no text. Please try again."
            )

        response_placeholder.markdown(answer)

    elapsed = time.perf_counter() - start_time

    st.session_state.last_latency = elapsed
    st.session_state.last_answer = answer

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

except Exception as error:
    st.error(t["error_model"])

    # التفاصيل للمطور فقط حتى يسهل تشخيص المشكلة
    with st.expander("Technical details"):
        st.code(str(error))

st.session_state.uploaded_version += 1
st.rerun()
```

# =====================================================

# 14. تذييل الصفحة

# =====================================================

st.markdown(
f'<div class="note">{html.escape(t["privacy"])}</div>',
unsafe_allow_html=True
)
