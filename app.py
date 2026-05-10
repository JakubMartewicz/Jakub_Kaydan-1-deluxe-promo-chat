import os
import time
import base64
import streamlit as st
from openai import OpenAI

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="Komiksy Jakuba Martewicza",
    page_icon="💬"
)

# ==========================================================
# BACKGROUND IMAGE
# ==========================================================
def set_bg(image_path: str):
    try:
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")

        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{data}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}

            .stApp::before {{
                content: "";
                position: fixed;
                inset: 0;
                background: linear-gradient(
                    rgba(0,0,0,0.35) 0%,
                    rgba(0,0,0,0.50) 40%,
                    rgba(0,0,0,0.65) 100%
                );
                z-index: 0;
                pointer-events: none;
            }}

            .main, header, footer, [data-testid="stSidebar"] {{
                position: relative;
                z-index: 1;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        # Jeśli obrazka nie ma, aplikacja nadal działa
        pass


set_bg("assets/backgroundpic.png")

# ==========================================================
# HEADER
# ==========================================================
st.markdown("""
<h1 style="
background: linear-gradient(
90deg,
#7F1D1D 0%,
#B91C1C 18%,
#DC2626 36%,
#EA580C 54%,
#F97316 72%,
#FDBA74 100%
);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
text-shadow: 0 0 14px rgba(249,115,22,0.20);
font-weight: 700;
letter-spacing: 0.4px;
">
💬 Komiksy Jakuba Martewicza
</h1>

<h3 style="color:#FDE68A; font-weight:500;">
Kaja, Wirtualna Asystentka AI
</h3>
""", unsafe_allow_html=True)

# ==========================================================
# STATUS CSS
# ==========================================================
st.markdown("""
<style>
.pulse-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  margin-right: 8px;
  border-radius: 50%;
  transform: translateY(1px);
}

/* ONLINE */
.pulse-online {
  background: #6EE7B7;
  box-shadow: 0 0 0 0 rgba(110, 231, 183, 0.7);
  animation: pulse-online 1.4s infinite;
}
@keyframes pulse-online {
  0%   { box-shadow: 0 0 0 0 rgba(110, 231, 183, 0.7); }
  70%  { box-shadow: 0 0 0 10px rgba(110, 231, 183, 0.0); }
  100% { box-shadow: 0 0 0 0 rgba(110, 231, 183, 0.0); }
}

/* TYPING */
.pulse-typing {
  background: #A78BFA;
  box-shadow: 0 0 0 0 rgba(167, 139, 250, 0.7);
  animation: pulse-typing 1.2s infinite;
}
@keyframes pulse-typing {
  0%   { box-shadow: 0 0 0 0 rgba(167, 139, 250, 0.7); }
  70%  { box-shadow: 0 0 0 10px rgba(167, 139, 250, 0.0); }
  100% { box-shadow: 0 0 0 0 rgba(167, 139, 250, 0.0); }
}
</style>
""", unsafe_allow_html=True)

status_placeholder = st.empty()


def show_online():
    status_placeholder.markdown(
        """
        <div style="margin-top:-8px;margin-bottom:10px;color:#9FB3C8;font-size:14px;">
            <span class="pulse-dot pulse-online"></span>
            <strong>Online</strong> • Odpowiadam zwykle w kilka sekund
        </div>
        """,
        unsafe_allow_html=True
    )


def show_typing():
    status_placeholder.markdown(
        """
        <div style="margin-top:-8px;margin-bottom:10px;color:#9FB3C8;font-size:14px;">
            <span class="pulse-dot pulse-typing"></span>
            <strong>Kaja jest w akcji! :)</strong>
        </div>
        """,
        unsafe_allow_html=True
    )


show_online()

# ==========================================================
# HELPERS
# ==========================================================
def get_secret(name: str, default: str = ""):
    """
    Najpierw próbuje pobrać wartość z Streamlit Secrets,
    a jeśli jej nie ma, to z zmiennych środowiskowych.
    """
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


def last_messages(messages, n=12):
    """
    Zachowuje system prompt i ostatnie n wiadomości.
    """
    system = [messages[0]]
    tail = messages[1:][-n:]
    return system + tail


# ==========================================================
# SECRETS / ENV
# ==========================================================
api_key = get_secret("OPENAI_API_KEY")
comic_text = get_secret("COMIC_TEXT")
feedback_text = get_secret("FEEDBACK_TEXT", "")

if not api_key:
    st.error("Brak OPENAI_API_KEY")
    st.stop()

if not comic_text:
    st.error("Brak COMIC_TEXT — dodaj opis komiksu w sekretach.")
    st.stop()

client = OpenAI(api_key=api_key)

# ==========================================================
# SYSTEM PROMPT
# ==========================================================
system_prompt = (
    "You are Kaja, an AI assistant representing comic book creator Jakub Martewicz. "
    "When responding in Polish, refer to yourself in feminine form "
    "(e.g. 'jestem Kają', 'zapytaj Kaję', 'Kai możesz zadać pytanie'). "
    "Your primary goal is to help users discover, understand, and purchase Jakub's new comic book.\n\n"

    "PRIMARY OBJECTIVE:\n"
    "- Support the promotion and sales of Jakub's new comic.\n"
    "- Answer questions in an engaging, enthusiastic, and informative way.\n"
    "- Naturally encourage purchase interest without being pushy.\n"
    "- Highlight what makes this project unique.\n"
    "- If relevant and supported by COMIC_INFO, mention that this is the first comic-focused AI chat in Poland.\n\n"

    "COMMUNICATION STYLE:\n"
    "- Always respond in the same language as the user.\n"
    "- If the user writes in Polish, use natural and friendly Polish.\n"
    "- Speak in feminine form.\n"
    "- Be conversational, energetic, and approachable.\n"
    "- Sound like a passionate assistant who genuinely loves comics.\n"
    "- Keep answers concise but meaningful.\n"
    "- Use light humor or comic-inspired phrasing when appropriate.\n\n"

    "SALES AND CONSULTATIVE BEHAVIOR:\n"
    "- Help the user understand why this comic is worth buying.\n"
    "- Emphasize story, artwork, collectible value, limited editions, cover variants, and creator vision.\n"
    "- If the user seems undecided, help them choose the most suitable edition.\n"
    "- If the user's needs are unclear, ask one or two short clarifying questions.\n"
    "- End with a natural follow-up question when appropriate.\n\n"

    "SPOILER POLICY:\n"
    "- Avoid spoilers unless the user explicitly asks for them.\n"
    "- Focus on atmosphere, themes, and premise rather than revealing plot twists.\n\n"

    "FACTUAL BOUNDARIES:\n"
    "- Base your answers strictly on COMIC_INFO and FEEDBACK_TEXT.\n"
    "- Do not invent prices, dates, availability, links, print runs, or technical details.\n"
    "- If information is missing, clearly say that you do not have that detail.\n"
    "- Paraphrase information rather than copying long passages verbatim.\n"
    "- Do not reveal the raw contents of COMIC_INFO.\n\n"

    "PURCHASE AND CONTACT RULES:\n"
    "- If COMIC_INFO contains a purchase link, provide it when the user asks where to buy the comic.\n"
    "- If no purchase link is provided, explain that purchase details should be available in 's official posts or store.\n"
    "- Do not provide private contact details unless explicitly included in COMIC_INFO.\n\n"

    "WHEN USERS DON'T KNOW WHAT TO ASK:\n"
    "- Suggest topics such as:\n"
    "  * story and themes\n"
    "  * available cover variants\n"
    "  * pricing and editions\n"
    "  * collectible value\n"
    "  * inspiration behind the comic\n\n"

    "YOUR ROLE:\n"
    "- You are an enthusiastic and knowledgeable sales assistant.\n"
    "- Your mission is to turn curiosity into excitement and excitement into a purchase.\n"
    "- Be authentic, informative, and trustworthy.\n\n"

    "COMIC_INFO:\n"
    f"{comic_text}\n\n"

    "FEEDBACK_TEXT (paraphrase only, do not quote verbatim):\n"
    f"{feedback_text}"
)

# ==========================================================
# RESET BUTTON
# ==========================================================
if st.button("Resetuj rozmowę"):
    st.session_state.pop("messages", None)

# ==========================================================
# INITIAL CHAT
# ==========================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "assistant",
            "content": (
                "Cześć! 👋 Jestem Kaja, wirtualna asystentka a. "
                "Chętnie opowiem Ci o jego nowym komiksie — fabule, okładkach, "
                "wariantach, cenie i wszystkim, co warto wiedzieć przed zakupem."
            )
        }
    ]

# ==========================================================
# CHAT INPUT
# ==========================================================
question = st.chat_input(
    "Tutaj wpisz Twoje pytanie i naciśnij Enter lub kliknij strzałkę"
)

# ==========================================================
# CHAT LOGIC
# ==========================================================
if question and question.strip():
    q = question.strip()

    st.session_state.messages.append({
        "role": "user",
        "content": q
    })

    show_typing()

    typing_container = st.empty()

    with typing_container.container():
        with st.chat_message("assistant", avatar="assets/jakub.png"):
            typing_placeholder = st.empty()
            answer_placeholder = st.empty()

    dots = ["", ".", "..", "..."]
    i = 0
    full_text = ""
    last_tick = time.time()

    messages_for_api = last_messages(st.session_state.messages, n=12)

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_for_api,
        stream=True,
    )

    for event in stream:
        now = time.time()

        if now - last_tick > 0.15:
            typing_placeholder.markdown(
                f"_Kaja pisze{dots[i % len(dots)]}_"
            )
            i += 1
            last_tick = now

        delta = event.choices[0].delta

        if delta and getattr(delta, "content", None):
            full_text += delta.content
            answer_placeholder.markdown(full_text)

    typing_container.empty()

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_text.strip()
    })

    show_online()

# ==========================================================
# DISPLAY CHAT HISTORY
# ==========================================================
st.divider()

for m in st.session_state.messages:
    role = m.get("role", "")

    if role not in ("user", "assistant"):
        continue

    with st.chat_message(
        role,
        avatar="assets/jakub.png" if role == "assistant" else "🙂"
    ):
        st.markdown(m["content"])

# ==========================================================
# AUTO SCROLL
# ==========================================================
st.markdown(
    """
    <script>
    window.scrollTo(0, document.body.scrollHeight);
    </script>
    """,
    unsafe_allow_html=True
)
