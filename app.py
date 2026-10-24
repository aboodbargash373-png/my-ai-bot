import os
import json
import time
import uuid

import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types


# ==========================================
# 1. إعدادات التطبيق
# ==========================================

st.set_page_config(
    page_title="RADDAD CYBER AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL_NAME = "gemini-3.8-flash"
MAX_HISTORY = 12


# ==========================================
# 2. اللغات
# ==========================================

TEXTS = {
    "العربية": {
        "subtitle": "وكيلك الذكي — متعدد الوسائط وسهل الاستخدام",
        "settings": "الإعدادات",
        "language": "اللغة",
        "theme": "المظهر",
        "dark": "داكن",
        "light": "فاتح",
        "thinking": "مستوى التفكير",
        "status": "حالة المحرك",
        "new": "محادثة جديدة",
        "clear": "مسح المحادثة",
        "export": "تصدير المحادثة",
        "shortcuts": "اختصارات سريعة",
        "track1": "📦 تتبع ORD-101",
        "track2": "📦 تتبع ORD-202",
        "services": "💡 الخدمات",
        "support": "🛠️ الدعم الفني",
        "files": "📁 الملفات",
        "camera": "📸 الكاميرا",
        "voice": "🎙️ الصوت",
        "file_hint": "ارفع صورة أو PDF أو ملف صوتي",
        "camera_hint": "التقط صورة بالكاميرا",
        "voice_hint": "سجّل رسالتك الصوتية",
        "placeholder": "اكتب رسالتك هنا...",
        "welcome": "أهلًا! أنا رداد ⚡ كيف بقدر أساعدك؟",
        "waiting": "رداد يفكر...",
        "missing_key": "مفتاح Gemini API غير موجود. أضفه في Secrets.",
        "api_error": "تعذر الاتصال بـ Gemini. افتح التفاصيل التقنية لمعرفة السبب.",
        "latency": "زمن الرد",
        "read": "🔊 استمع للرد",
        "privacy": "المحادثة لا تُحفظ في قاعدة بيانات خارجية.",
        "services_answer": (
            "الخدمات المتاحة:\n"
            "• الإجابة عن الأسئلة\n"
            "• تحليل الصور والملفات والصوت\n"
            "• تتبع الطلبات التجريبية\n"
            "• المساعدة في المشاكل التقنية"
        ),
        "demo": "ملاحظة: بيانات الطلبات تجريبية وغير متصلة بنظام حقيقي.",
        "support_prompt": "أحتاج إلى مساعدة في مشكلة تقنية.",
        "file_error": "تعذر التعامل مع الملف",
        "empty": "اكتب رسالة أو أرفق ملفًا.",
    },

    "English": {
        "subtitle": "Your intelligent multimodal assistant",
        "settings": "Settings",
        "language": "Language",
        "theme": "Appearance",
        "dark": "Dark",
        "light": "Light",
        "thinking": "Reasoning level",
        "status": "Engine status",
        "new": "New conversation",
        "clear": "Clear conversation",
        "export": "Export conversation",
        "shortcuts": "Quick actions",
        "track1": "📦 Track ORD-101",
        "track2": "📦 Track ORD-202",
        "services": "💡 Services",
        "support": "🛠️ Support",
        "files": "📁 Files",
        "camera": "📸 Camera",
        "voice": "🎙️ Voice",
        "file_hint": "Upload an image, PDF, or audio file",
        "camera_hint": "Take a picture",
        "voice_hint": "Record a voice message",
        "placeholder": "Type your message here...",
        "welcome": "Welcome! I'm Raddad ⚡ How can I help?",
        "waiting": "Raddad is thinking...",
        "missing_key": "Gemini API key is missing. Add it to Secrets.",
        "api_error": "Gemini connection failed. Open technical details.",
        "latency": "Response time",
        "read": "🔊 Read response aloud",
        "privacy": "Chats are not saved to an external database.",
        "services_answer": (
            "Available services:\n"
            "• General questions\n"
            "• Image, file, and audio analysis\n"
            "• Demo order tracking\n"
            "• Technical assistance"
        ),
        "demo": "Note: order data is demo data, not connected to a real system.",
        "support_prompt": "I need help with a technical issue.",
        "file_error": "Could not process file",
        "empty": "Write a message or attach a file.",
    },
}


# ==========================================
# 3. بيانات الجلسة
# ==========================================

def init_state(key, value):
    if key not in st.session_state:
        st.session_state[key] = value


init_state("language", "العربية")
init_state("theme", "Dark")
init_state("messages", [])
init_state("last_latency", None)
init_state("pending_prompt", "")
init_state("upload_version", 0)


# ==========================================
# 4. التصميم
# ==========================================

dark = st.session_state.theme == "Dark"

if dark:
    bg = "#07111F"
    panel = "#0D1B2D"
    card = "#10243A"
    fg = "#E5EDF7"
    muted = "#9BAFC7"
    border = "#203A57"
    accent = "#45B8FF"
else:
    bg = "#F2F6FC"
    panel = "#FFFFFF"
    card = "#E8F1FC"
    fg = "#15243A"
    muted = "#526780"
    border = "#D2DFEF"
    accent = "#087BC1"

rtl = st.session_state.language == "العربية"
direction = "rtl" if rtl else "ltr"
alignment = "right" if rtl else "left"

st.markdown(
    f"""
    <style>
    @import url(
      'https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap'
    );

    html, body, [class*="css"] {{
        font-family: 'Cairo', sans-serif;
    }}

    .stApp {{
        background: {bg};
        color: {fg};
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
        background: {panel};
        border-right: 1px solid {border};
    }}

    .hero {{
        padding: 28px;
        border-radius: 22px;
        border: 1px solid {border};
        background: linear-gradient(135deg, {panel}, {card});
        margin-bottom: 20px;
        direction: {direction};
        text-align: {alignment};
    }}

    .hero h1 {{
        color: {accent};
        font-size: clamp(26px, 4vw, 42px);
        font-weight: 800;
        margin: 0;
    }}

    .hero p {{
        color: {muted};
        margin-top: 10px;
    }}

    .badge {{
        display: inline-block;
        padding: 5px 12px;
        border: 1px solid {border};
        border-radius: 50px;
        color: {accent};
        font-size: 12px;
        margin-top: 10px;
    }}

    .metric {{
        background: {panel};
        border: 1px solid {border};
        padding: 14px;
        border-radius: 15px;
        text-align: center;
        min-height: 78px;
    }}

    .metric-value {{
        color: {accent};
        font-size: 18px;
        font-weight: 800;
    }}

    .metric-label {{
        color: {muted};
        font-size: 12px;
        margin-top: 4px;
    }}

    div[data-testid="stChatMessage"] {{
        background: {panel};
        border: 1px solid {border};
        border-radius: 16px;
        padding: 12px;
        margin-bottom: 10px;
    }}

    .stButton button {{
        border-radius: 12px;
        border: 1px solid {border};
        min-height: 42px;
    }}

    .stButton button:hover {{
        border-color: {accent};
        color: {accent};
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 10px;
        padding: 9px 12px;
    }}

    .small-note {{
        text-align: center;
        color: {muted};
        font-size: 12px;
        padding: 12px 0;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# 5. مفتاح API
# ==========================================

API_KEY = os.getenv("GEMINI_API_KEY", "")

try:
    if not API_KEY:
        API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    pass


@st.cache_resource(show_spinner=False)
def get_client(key):
    return genai.Client(api_key=key)


# ==========================================
# 6. الطلبات التجريبية
# ==========================================

ORDERS = {
    "ORD-101": {
        "ar": "طلبك قيد الشحن. الموعد التجريبي المتوقع خلال 48 ساعة.",
        "en": "Your order is shipping. Demo ETA: 48 hours.",
    },
    "ORD-202": {
        "ar": "تم تجهيز الطلب وهو بانتظار شركة الشحن.",
        "en": "Your order is prepared and waiting for shipping.",
    },
    "ORD-303": {
        "ar": "تم تسليم الطلب بنجاح.",
        "en": "Your order was delivered successfully.",
    },
}


def local_action(prompt, language):
    upper = prompt.upper()
    lower = prompt.lower()

    for order_id, data in ORDERS.items():
        if order_id in upper:
            key = "ar" if language == "العربية" else "en"
            return (
                f"{order_id}: {data[key]}\n\n"
                f"{TEXTS[language]['demo']}"
            )

    service_terms = [
        "الخدمات",
        "خدماتكم",
        "شو بتقدم",
        "ماذا تقدم",
        "services",
        "what can you do",
    ]

    if any(term in lower for term in service_terms):
        return TEXTS[language]["services_answer"]

    return None


def get_system_instruction(language):
    if language == "العربية":
        return """
أنت رداد RADDAD CYBER AI، مساعد ذكي احترافي.

- أجب بالعربية ما لم يطلب المستخدم لغة أخرى.
- كن دقيقًا ومباشرًا.
- لا تخترع معلومات أو تدّعي تنفيذ عمليات لم تحدث.
- حلل الصور والملفات المرفقة اعتمادًا على محتواها.
- إذا لم تعرف الإجابة، وضّح ذلك.
- بيانات الطلبات في التطبيق تجريبية.
- اجعل الردود مختصرة افتراضيًا، وفصّل عند الطلب.
"""
    return """
You are RADDAD CYBER AI, a professional intelligent assistant.

- Respond in the user's language.
- Be accurate, clear, and concise.
- Never invent facts or claim actions you did not perform.
- Analyze attached files using their actual content.
- State clearly when you do not know something.
- Order data in this application is demo data.
"""


# ==========================================
# 7. القائمة الجانبية
# ==========================================

with st.sidebar:
    st.markdown("## ⚡ RADDAD CYBER AI")
    st.caption("SMART MULTIMODAL AGENT")
    st.divider()

    t = TEXTS[st.session_state.language]
    st.markdown(f"### ⚙️ {t['settings']}")

    language = st.selectbox(
        t["language"],
        ["العربية", "English"],
        index=["العربية", "English"].index(
            st.session_state.language
        ),
        key="language_select",
    )

    if language != st.session_state.language:
        st.session_state.language = language
        st.rerun()

    t = TEXTS[st.session_state.language]

    theme = st.selectbox(
        t["theme"],
        ["Dark", "Light"],
        index=["Dark", "Light"].index(
            st.session_state.theme
        ),
        format_func=lambda x: (
            t["dark"] if x == "Dark" else t["light"]
        ),
        key="theme_select",
    )

    if theme != st.session_state.theme:
        st.session_state.theme = theme
        st.rerun()

    thinking_level = st.selectbox(
        t["thinking"],
        ["low", "medium", "high"],
        index=0,
    )

    st.divider()
    st.markdown(f"### 🤖 {t['status']}")

    if API_KEY:
        st.success("API key loaded")
    else:
        st.error(t["missing_key"])

    st.code(MODEL_NAME)

    if st.session_state.last_latency is not None:
        st.metric(
            t["latency"],
            f"{st.session_state.last_latency:.2f} s",
        )

    if st.button(t["new"], use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_latency = None
        st.session_state.pending_prompt = ""
        st.session_state.upload_version += 1
        st.rerun()

    if st.button(t["clear"], use_container_width=True):
        st.session_state.messages = []
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
            use_container_width=True,
        )


# ==========================================
# 8. العنوان والإحصائيات
# ==========================================

t = TEXTS[st.session_state.language]

st.markdown(
    f"""
    <div class="hero">
        <h1>⚡ RADDAD CYBER AI</h1>
        <p>{t['subtitle']}</p>
        <span class="badge">● {MODEL_NAME}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="metric">
            <div class="metric-value">AI</div>
            <div class="metric-label">SMART AGENT</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    latency = (
        f"{st.session_state.last_latency:.2f} s"
        if st.session_state.last_latency is not None
        else "Ready"
    )

    st.markdown(
        f"""
        <div class="metric">
            <div class="metric-value">{latency}</div>
            <div class="metric-label">{t['latency']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    status = "ONLINE" if API_KEY else "API KEY NEEDED"

    st.markdown(
        f"""
        <div class="metric">
            <div class="metric-value">{status}</div>
            <div class="metric-label">SYSTEM STATUS</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================
# 9. الاختصارات
# ==========================================

st.markdown(f"### {t['shortcuts']}")

quick_cols = st.columns(4)

if st.session_state.language == "العربية":
    quick_prompts = [
        "ما حالة الطلب ORD-101؟",
        "ما حالة الطلب ORD-202؟",
        "ما الخدمات التي تقدمها؟",
        t["support_prompt"],
    ]
else:
    quick_prompts = [
        "What is the status of order ORD-101?",
        "What is the status of order ORD-202?",
        "What services do you provide?",
        t["support_prompt"],
    ]

quick_labels = [
    t["track1"],
    t["track2"],
    t["services"],
    t["support"],
]

for i, col in enumerate(quick_cols):
    with col:
        if st.button(
            quick_labels[i],
            use_container_width=True,
            key=f"quick_{i}",
        ):
            st.session_state.pending_prompt = quick_prompts[i]
            st.rerun()


# ==========================================
# 10. سجل المحادثة
# ==========================================

if not st.session_state.messages:
    st.info(t["welcome"])

for i, message in enumerate(st.session_state.messages):
    role = message["role"]

    with st.chat_message(
        role,
        avatar="⚡" if role == "assistant" else "👤",
    ):
        st.markdown(message["content"])

        if role == "assistant" and message["content"]:
            if st.button(t["read"], key=f"read_{i}"):
                text_json = json.dumps(
                    message["content"],
                    ensure_ascii=False,
                )

                lang_code = (
                    "ar-SA"
                    if st.session_state.language == "العربية"
                    else "en-US"
                )

                components.html(
                    f"""
                    <script>
                    if ("speechSynthesis" in window) {{
                        window.speechSynthesis.cancel();
                        const speech = new SpeechSynthesisUtterance(
                            {text_json}
                        );
                        speech.lang = "{lang_code}";
                        speech.rate = 1;
                        window.speechSynthesis.speak(speech);
                    }}
                    </script>
                    """,
                    height=0,
                )


# ==========================================
# 11. الملفات والكاميرا والصوت
# ==========================================

st.divider()

tab_files, tab_camera, tab_voice = st.tabs(
    [t["files"], t["camera"], t["voice"]]
)

with tab_files:
    uploaded_files = st.file_uploader(
        t["file_hint"],
        type=[
            "png", "jpg", "jpeg", "webp",
            "pdf",
            "mp3", "wav", "m4a", "ogg", "aac", "flac",
        ],
        accept_multiple_files=True,
        key=f"files_{st.session_state.upload_version}",
    )

    if uploaded_files:
        for file in uploaded_files:
            st.caption(f"📎 {file.name}")

            if file.type and file.type.startswith("image/"):
                st.image(
                    file,
                    caption=file.name,
                    use_container_width=True,
                )

with tab_camera:
    camera_photo = st.camera_input(
        t["camera_hint"],
        key=f"camera_{st.session_state.upload_version}",
    )

with tab_voice:
    audio_data = st.audio_input(
        t["voice_hint"],
        key=f"audio_{st.session_state.upload_version}",
    )

    if audio_data:
        st.audio(audio_data)


# ==========================================
# 12. إرسال الرسالة
# ==========================================

chat_text = st.chat_input(t["placeholder"])

if chat_text:
    st.session_state.pending_prompt = chat_text

prompt = st.session_state.pending_prompt

has_files = (
    bool(uploaded_files)
    or camera_photo is not None
    or audio_data is not None
)

if prompt or has_files:

    if not prompt:
        if st.session_state.language == "العربية":
            prompt = (
                "حلل الملفات المرفقة وأخبرني بمحتواها. "
                "استمع للتسجيل الصوتي وأجب عنه إذا وُجد."
            )
        else:
            prompt = (
                "Analyze the attached files and describe their content. "
                "Listen to and respond to the audio if present."
            )

    st.session_state.pending_prompt = ""

    language = st.session_state.language
    t = TEXTS[language]

    user_display = prompt

    if audio_data:
        user_display += (
            "\n🎙️ [تسجيل صوتي مرفق]"
            if language == "العربية"
            else "\n🎙️ [Audio attached]"
        )

    st.session_state.messages.append({
        "role": "user",
        "content": user_display,
    })

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

        if uploaded_files:
            for file in uploaded_files:
                st.caption("📎 " + file.name)

        if camera_photo is not None:
            st.image(camera_photo, width=250)

        if audio_data is not None:
            st.audio(audio_data)

    # --------------------------------------
    # معالجة الطلبات السريعة محليًا
    # --------------------------------------

    quick_result = local_action(prompt, language)

    if quick_result:
        with st.chat_message("assistant", avatar="⚡"):
            st.markdown(quick_result)

        st.session_state.messages.append({
            "role": "assistant",
            "content": quick_result,
        })

        st.session_state.upload_version += 1
        st.rerun()

    # --------------------------------------
    # التحقق من المفتاح
    # --------------------------------------

    if not API_KEY:
        st.error(t["missing_key"])
        st.stop()

    started = time.perf_counter()

    try:
        client = get_client(API_KEY)

        # سجل مختصر للمحادثة لتقليل حجم الطلب
        previous_messages = (
            st.session_state.messages[:-1][-MAX_HISTORY:]
        )

        contents = []

        for old in previous_messages:
            contents.append(
                types.Content(
                    role=(
                        "model"
                        if old["role"] == "assistant"
                        else "user"
                    ),
                    parts=[
                        types.Part.from_text(
                            text=old["content"]
                        )
                    ],
                )
            )

        current_parts = [
            types.Part.from_text(text=prompt)
        ]

        # الملفات المرفقة
        if uploaded_files:
            for file in uploaded_files:
                mime_type = (
                    file.type or "application/octet-stream"
                )

                supported = (
                    mime_type.startswith("image/")
                    or mime_type.startswith("audio/")
                    or mime_type == "application/pdf"
                )

                if not supported:
                    st.warning(
                        f"{t['file_error']}: {file.name}"
                    )
                    continue

                current_parts.append(
                    types.Part.from_bytes(
                        data=file.getvalue(),
                        mime_type=mime_type,
                    )
                )

        # صورة الكاميرا
        if camera_photo is not None:
            current_parts.append(
                types.Part.from_bytes(
                    data=camera_photo.getvalue(),
                    mime_type="image/jpeg",
                )
            )

        # التسجيل الصوتي
        if audio_data is not None:
            current_parts.append(
                types.Part.from_bytes(
                    data=audio_data.getvalue(),
                    mime_type=audio_data.type or "audio/wav",
                )
            )

        contents.append(
            types.Content(
                role="user",
                parts=current_parts,
            )
        )

        # لا نستخدم temperature مع Gemini 3.8 Flash
        config = types.GenerateContentConfig(
            system_instruction=get_system_instruction(language),
            max_output_tokens=2048,
            thinking_config=types.ThinkingConfig(
                thinking_level=thinking_level
            ),
        )

        # عرض الرد تدريجيًا
        with st.chat_message("assistant", avatar="⚡"):
            answer_box = st.empty()
            answer_parts = []

            with st.spinner(t["waiting"]):
                stream = client.models.generate_content_stream(
                    model=MODEL_NAME,
                    contents=contents,
                    config=config,
                )

                for chunk in stream:
                    if chunk.text:
                        answer_parts.append(chunk.text)

                        answer_box.markdown(
                            "".join(answer_parts) + " ▌"
                        )

            answer = "".join(answer_parts).strip()

            if not answer:
                answer = (
                    "لم يصل رد نصي من النموذج. جرّب مرة ثانية."
                    if language == "العربية"
                    else "The model returned no text. Please try again."
                )

            answer_box.markdown(answer)

        st.session_state.last_latency = (
            time.perf_counter() - started
        )

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
        })

    except Exception as error:
        st.error(t["api_error"])

        with st.expander("Technical details"):
            st.code(str(error))

    st.session_state.upload_version += 1
    st.rerun()


# ==========================================
# 13. تذييل
# ==========================================

st.markdown(
    f'<div class="small-note">🔒 {TEXTS[st.session_state.language]["privacy"]}</div>',
    unsafe_allow_html=True,
)
