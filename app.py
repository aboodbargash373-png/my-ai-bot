import os
import time
from io import BytesIO

import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

# إعدادات الصفحة
st.set_page_config(
    page_title="RADDAD CYBER AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم الواجهة
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap');

.stApp {
    background: radial-gradient(ellipse at top, #101a32 0%, #080b13 60%, #070910 100%);
    color: #e5edf8;
    font-family: 'IBM Plex Sans Arabic', 'Segoe UI', sans-serif;
}

section[data-testid="stSidebar"] {
    background: rgba(10, 15, 28, 0.96);
    border-right: 1px solid #18344a;
}

.block-container {
    max-width: 1120px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

.hero {
    text-align: center;
    padding: 1rem 0;
}

.hero h1 {
    font-size: clamp(2rem, 5vw, 3.2rem);
    font-weight: 900;
    background: linear-gradient(110deg, #22d3ee, #60a5fa, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    color: #9db2ce;
}

.metric-wrap {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
    margin: 1.5rem 0;
}

.metric {
    background: rgba(15, 30, 51, 0.85);
    border: 1px solid rgba(34, 211, 238, 0.25);
    border-radius: 16px;
    padding: 15px;
    text-align: center;
}

.metric b {
    display: block;
    color: #22d3ee;
}

.metric span {
    color: #94a3b8;
    font-size: 0.8rem;
}

.stButton > button {
    border-radius: 14px;
    border: 1px solid #155e75;
    background: linear-gradient(120deg, #102334, #111b30);
    color: #67e8f9;
    font-weight: 600;
    min-height: 2.7rem;
}

.stButton > button:hover {
    border-color: #22d3ee;
    background: #12344a;
}

[data-testid="stChatMessage"] {
    border: 1px solid rgba(100, 116, 139, 0.15);
    border-radius: 16px;
    background: rgba(12, 18, 31, 0.55);
    padding: 0.8rem;
}

.small-note {
    color: #94a3b8;
    font-size: 0.8rem;
    text-align: center;
    margin-top: 1rem;
}

@media(max-width: 640px) {
    .metric-wrap {
        grid-template-columns: 1fr;
    }
}
</style>
""", unsafe_allow_html=True)


# إعدادات التحكم
with st.sidebar:
    st.markdown("## ⚙️ لوحة التحكم")

    language = st.selectbox(
        "اللغة / Language",
        ["العربية", "English"]
    )

    creativity = st.slider(
        "مستوى الإبداع",
        0.0, 1.0, 0.4, 0.1
    )

    model_name = st.selectbox(
        "نموذج الذكاء الاصطناعي",
        ["gemini-3.8-flash", "gemini-2.0-flash"]
    )

    st.markdown("---")

    if st.button("🧹 محادثة جديدة", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_latency = None
        st.rerun()

is_ar = language == "العربية"


# مفتاح API
try:
    api_key = st.secrets.get("GEMINI_API_KEY")
except Exception:
    api_key = None

api_key = api_key or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("لم يتم العثور على GEMINI_API_KEY. أضفه إلى Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)


# أدوات الوكيل الذكي
ORDERS = {
    "ORD-101": "طلبك قيد الشحن حالياً، ومن المتوقع وصوله خلال 48 ساعة.",
    "ORD-202": "تم تجهيز الطلب وهو بانتظار شركة الشحن.",
    "ORD-303": "تم تسليم الطلب بنجاح."
}


def check_order_status(order_id: str) -> dict:
    """التحقق من حالة الطلب باستخدام رقمه."""

    order_id = order_id.strip().upper()

    if order_id in ORDERS:
        return {
            "found": True,
            "order_id": order_id,
            "status": ORDERS[order_id],
            "demo": True
        }

    return {
        "found": False,
        "order_id": order_id,
        "message": "رقم الطلب غير موجود في بيانات العرض التجريبية.",
        "demo": True
    }


def list_services() -> dict:
    """عرض الخدمات المتوفرة."""

    return {
        "services": [
            "الإجابة عن الأسئلة",
            "تحليل الصور",
            "فهم الرسائل الصوتية المدعومة",
            "تتبع الطلبات التجريبية",
            "المساعدة التقنية"
        ]
    }


def create_support_ticket(
    summary: str,
    priority: str = "normal"
) -> dict:
    """إنشاء مسودة تجريبية لتذكرة دعم."""

    summary = summary.strip()[:500]

    if not summary:
        return {"created": False, "message": "اكتب وصف المشكلة أولاً."}

    if priority not in ["low", "normal", "high"]:
        priority = "normal"

    return {
        "created": True,
        "ticket_id": f"DEMO-{int(time.time())}",
        "priority": priority,
        "summary": summary,
        "note": "هذه مسودة تجريبية وليست تذكرة مرسلة إلى شركة."
    }


# تعليمات الوكيل
if is_ar:
    system_instruction = """
    أنت رداد، وكيل ذكاء اصطناعي مساعد واحترافي.

    قواعدك:
    1. أجب باللغة العربية إذا تحدث المستخدم بالعربية.
    2. كن واضحاً ومختصراً.
    3. استخدم أداة تتبع الطلبات عندما يسأل المستخدم عن طلب.
    4. استخدم أداة الخدمات عند السؤال عن الخدمات.
    5. استخدم أداة الدعم عند طلب إنشاء مسودة تذكرة.
    6. لا تخترع نتائج الأدوات.
    7. وضح أن الطلبات وتذاكر الدعم تجريبية.
    8. حلل الصور المرفقة إذا كانت ذات صلة بالسؤال.
    9. لا تدّعِ تنفيذ إجراءات خارجية لم تنفذها فعلياً.
    """
else:
    system_instruction = """
    You are Raddad, a helpful and professional AI agent.
    Answer clearly and concisely in the user's language.
    Use tools when appropriate for orders, services, and support drafts.
    Never invent tool results or claim external actions occurred.
    Order records and support tickets are demo-only.
    Analyze attached images when relevant.
    """


# تهيئة سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_latency" not in st.session_state:
    st.session_state.last_latency = None


# العنوان
title = "RADDAD CYBER AI"

subtitle = (
    "وكيل ذكاء اصطناعي متعدد الوسائط والخدمات"
    if is_ar else
    "Multimodal Artificial Intelligence Agent"
)

st.markdown(
    f"""
    <div class="hero">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """,
    unsafe_allow_html=True
)


# المؤشرات
latency = st.session_state.last_latency

latency_text = (
    f"{latency:.2f} ثانية"
    if is_ar and latency is not None else
    f"{latency:.2f} s"
    if latency is not None else
    "جاهز"
    if is_ar else
    "Ready"
)

st.markdown(
    f"""
    <div class="metric-wrap">
        <div class="metric">
            <b>{"وكيل ذكي" if is_ar else "AI Agent"}</b>
            <span>{"استخدام الأدوات" if is_ar else "Tool calling"}</span>
        </div>
        <div class="metric">
            <b>{latency_text}</b>
            <span>{"زمن الاستجابة" if is_ar else "Response time"}</span>
        </div>
        <div class="metric">
            <b>{"نشط" if is_ar else "ONLINE"}</b>
            <span>{"حالة النظام" if is_ar else "System status"}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# عرض المحادثة السابقة
for msg in st.session_state.messages:
    with st.chat_message(
        msg["role"],
        avatar="⚡" if msg["role"] == "assistant" else "👤"
    ):
        st.markdown(msg["content"])


# الاختصارات
st.markdown("#### 🚀 اختصارات سريعة")

c1, c2, c3, c4 = st.columns(4)

quick_prompt = None

with c1:
    if st.button("📦 تتبع ORD-101", use_container_width=True):
        quick_prompt = "تحقق من حالة الطلب ORD-101"

with c2:
    if st.button("📦 تتبع ORD-202", use_container_width=True):
        quick_prompt = "تحقق من حالة الطلب ORD-202"

with c3:
    if st.button("💡 الخدمات", use_container_width=True):
        quick_prompt = "ما الخدمات المتوفرة؟"

with c4:
    if st.button("🛠️ الدعم", use_container_width=True):
        quick_prompt = "ساعدني بإنشاء مسودة تذكرة دعم لمشكلة تقنية."


# رفع الصور والصوت
with st.expander("📎 إرفاق صورة أو ملف صوتي"):

    uploaded_image = st.file_uploader(
        "اختر صورة",
        type=["png", "jpg", "jpeg", "webp"]
    )

    image_data = None

    if uploaded_image:
        try:
            image_data = Image.open(uploaded_image).convert("RGB")
            st.image(image_data, use_container_width=True)
        except Exception:
            st.warning("تعذر فتح الصورة.")

    audio_file = st.file_uploader(
        "اختر ملفاً صوتياً",
        type=["wav", "mp3", "m4a"]
    )

    if audio_file:
        st.audio(audio_file)


# استقبال الرسالة
placeholder = (
    "اكتب سؤالك أو رقم الطلب مثل ORD-101..."
    if is_ar else
    "Ask a question or enter an order ID..."
)

typed_prompt = st.chat_input(placeholder)

prompt = quick_prompt or typed_prompt


# تنفيذ الطلب
if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # إرسال آخر الرسائل فقط لتقليل حجم السياق
    recent_messages = st.session_state.messages[-12:]

    contents = []

    for message in recent_messages:
        role = (
            "user"
            if message["role"] == "user"
            else "model"
        )

        contents.append(
            types.Content(
                role=role,
                parts=[
                    types.Part.from_text(
                        text=message["content"]
                    )
                ]
            )
        )

    # إرفاق الوسائط بالرسالة الحالية
    if image_data is not None or audio_file is not None:

        parts = [types.Part.from_text(text=prompt)]

        if image_data is not None:
            image_buffer = BytesIO()

            image_data.save(
                image_buffer,
                format="JPEG",
                quality=85
            )

            parts.append(
                types.Part.from_bytes(
                    data=image_buffer.getvalue(),
                    mime_type="image/jpeg"
                )
            )

        if audio_file is not None:
            parts.append(
                types.Part.from_bytes(
                    data=audio_file.getvalue(),
                    mime_type=audio_file.type or "audio/wav"
                )
            )

        contents[-1] = types.Content(
            role="user",
            parts=parts
        )

    with st.chat_message("assistant", avatar="⚡"):

        with st.spinner(
            "رداد يفكر..." if is_ar else "Raddad is thinking..."
        ):

            start_time = time.perf_counter()

            try:

                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=creativity,
                        max_output_tokens=900,
                        tools=[
                            check_order_status,
                            list_services,
                            create_support_ticket
                        ]
                    )
                )

                answer = (response.text or "").strip()

                if not answer:
                    answer = (
                        "لم أتمكن من إنشاء إجابة. حاول مرة أخرى."
                        if is_ar else
                        "I couldn't generate an answer. Please try again."
                    )

                st.session_state.last_latency = (
                    time.perf_counter() - start_time
                )

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as error:

                error_text = str(error).lower()

                if "429" in error_text or "quota" in error_text:
                    answer = (
                        "وصلت إلى حد استخدام API. حاول لاحقاً."
                        if is_ar else
                        "API quota reached. Please try later."
                    )

                elif "404" in error_text or "not found" in error_text:
                    answer = (
                        "النموذج غير متاح لمفتاحك. اختر نموذجاً آخر."
                        if is_ar else
                        "The model is unavailable. Choose another model."
                    )

                else:
                    answer = (
                        "حدث خطأ أثناء الاتصال. تحقق من مفتاح API والإنترنت."
                        if is_ar else
                        "Connection error. Check your API key and internet."
                    )

                st.error(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })


st.markdown(
    '<div class="small-note">🔐 حافظ على سرية مفتاح API ولا ترفعه إلى GitHub.</div>',
    unsafe_allow_html=True
)
