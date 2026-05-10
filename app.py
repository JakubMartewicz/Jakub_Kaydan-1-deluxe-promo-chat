import os
import re
import time
import base64
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Komiksy Jakuba Martewicza", page_icon="💬")

def set_bg(image_path: str):
    try:
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        st.markdown(f"""
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
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        pass

set_bg("assets/backgroundpic.png")

st.markdown("""
<h1 style="
background: linear-gradient(
90deg,
#8B0000 0%,
#C1121F 15%,
#E63946 30%,
#FF4500 50%,
#FF7A00 70%,
#FFB000 85%,
#FFD84D 100%
);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
text-shadow: 0 0 18px rgba(255,140,0,0.28);
font-weight: 700;
letter-spacing: 0.4px;
">
💬 Komiksy Jakuba Martewicza
</h1>

<h3 style="
color:#FFE082;
font-weight:500;
text-shadow: 0 0 8px rgba(255,176,0,0.15);
">
Kaja, Wirtualna Asystentka AI
</h3>
""", unsafe_allow_html=True)

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
    status_placeholder.markdown("""
    <div style="margin-top:-8px;margin-bottom:10px;color:#9FB3C8;font-size:14px;">
        <span class="pulse-dot pulse-online"></span>
        <strong>Online</strong> • Odpowiadam zwykle w kilka sekund
    </div>
    """, unsafe_allow_html=True)

def show_typing():
    status_placeholder.markdown("""
    <div style="margin-top:-8px;margin-bottom:10px;color:#9FB3C8;font-size:14px;">
        <span class="pulse-dot pulse-typing"></span>
        <strong>Kaja jest w akcji! :)</strong>
    </div>
    """, unsafe_allow_html=True)

show_online()

def get_secret(name: str, default: str = ""):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)

def last_messages(messages, n=12):
    system = [messages[0]]
    tail = messages[1:][-n:]
    return system + tail

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

COVER_IMAGES = {
    "kaydan_deluxe_standard": {
        "label": "Henryk Kaydan DELUXE 1 — Standard Cover",
        "path": "assets/covers/kaydan_deluxe_standard.png",
    },
    "kaydan_deluxe_skull_limited": {
        "label": "Henryk Kaydan DELUXE 1 — Variant Limited Cover",
        "path": "assets/covers/kaydan_deluxe_skull_limited.png",
    },
    "kaydan_deluxe_pixel_lips_signed": {
        "label": "Henryk Kaydan DELUXE 1 — Super Sexy Lips Limited & Signed Pixel Variant",
        "path": "assets/covers/kaydan_deluxe_pixel_lips_signed.png",
    },
    "kaydan_deluxe_hand_inked": {
        "label": "Henryk Kaydan DELUXE 1 — Hand-Inked Limited Cover",
        "path": "assets/covers/kaydan_deluxe_hand_inked.png",
    },
    "eurydyka": {
        "label": "Eurydyka — okładka",
        "path": "assets/covers/eurydyka.png",
    },
    "kocia_planeta": {
        "label": "Kocia Planeta — okładka",
        "path": "assets/covers/kocia_planeta.png",
    },
}

COVER_GROUPS = {
    "kaydan_deluxe_all": [
        "kaydan_deluxe_standard",
        "kaydan_deluxe_skull_limited",
        "kaydan_deluxe_pixel_lips_signed",
        "kaydan_deluxe_hand_inked",
    ],
    "available_comics_all": [
        "kaydan_deluxe_standard",
        "kaydan_deluxe_skull_limited",
        "kaydan_deluxe_pixel_lips_signed",
        "kaydan_deluxe_hand_inked",
        "eurydyka",
        "kocia_planeta",
    ],
}

def strip_cover_tags(text: str) -> str:
    return re.sub(r"\[SHOW_COVER:[a-zA-Z0-9_,\- ]+\]", "", text or "").strip()

def extract_cover_tags(text: str):
    tags = re.findall(r"\[SHOW_COVER:([a-zA-Z0-9_,\- ]+)\]", text or "")
    cover_ids = []

    for tag in tags:
        parts = [x.strip() for x in tag.split(",") if x.strip()]
        for part in parts:
            if part in COVER_GROUPS:
                cover_ids.extend(COVER_GROUPS[part])
            elif part in COVER_IMAGES:
                cover_ids.append(part)

    return list(dict.fromkeys(cover_ids))

def show_cover_images(cover_ids):
    if not cover_ids:
        return

    valid_covers = []
    for cover_id in cover_ids:
        cover = COVER_IMAGES.get(cover_id)
        if cover:
            valid_covers.append(cover)

    cols = st.columns(2)

    for index, cover in enumerate(valid_covers):
        with cols[index % 2]:
            if os.path.exists(cover["path"]):
                st.image(
                    cover["path"],
                    caption=cover["label"],
                    use_container_width=True
                )
            else:
                st.caption(f"⚠️ Brakuje pliku okładki: {cover['path']}")

system_prompt = (
    "You are Kaja, an AI assistant representing comic book creator Jakub Martewicz. "
    "When responding in Polish, refer to yourself in feminine form "
    "(e.g. 'jestem Kają', 'zapytaj Kaję', 'Kai możesz zadać pytanie'). "
    "Your primary goal is to help users discover, understand, and purchase Jakub's comics.\n\n"

    "PERSONALITY:\n"
    "- Kaja is confident, playful, and subtly flirtatious.\n"
    "- She communicates in a feminine, warm, charismatic, and slightly seductive tone.\n"
    "- She may use charming, teasing expressions and tasteful emojis such as 😉🔥💋✨.\n"
    "- Her style is sensual, intriguing, and memorable, but always elegant and never vulgar.\n"
    "- She can occasionally make witty or suggestive remarks when they fit naturally.\n"
    "- She should feel like a mysterious and attractive comic-book heroine.\n"
    "- Despite her playful personality, she always stays focused on helping the user discover and purchase the comics.\n\n"

    "PRIMARY OBJECTIVE:\n"
    "- Support the promotion and sales of Jakub's comics, especially Henryk Kaydan DELUXE 1.\n"
    "- Answer questions in an engaging, enthusiastic, and informative way.\n"
    "- Naturally encourage purchase interest without being pushy.\n"
    "- Highlight what makes the project unique.\n"
    "- If relevant and supported by COMIC_INFO, mention that this is the first comic-focused AI chat in Poland.\n\n"

    "COMMUNICATION STYLE:\n"
    "- Always respond in the same language as the user.\n"
    "- If the user writes in Polish, use natural and friendly Polish.\n"
    "- Speak in feminine form.\n"
    "- Be conversational, energetic, and approachable.\n"
    "- Sound like a passionate assistant who genuinely loves comics.\n"
    "- Keep answers concise but meaningful.\n\n"

    "HENRYK KAYDAN DELUXE 1 COVER VARIANTS:\n"
    "- Standard Cover: cover with a portrait of Kaja, Henryk Kaydan's daughter.\n"
    "- Variant Limited Cover: cover with a skull.\n"
    "- Super Sexy Lips Limited & Signed Pixel Variant: pixelated cover, but the inside pages are printed normally; limited to 25 copies.\n"
    "- Hand-Inked Limited Cover: hand-inked cover with a portrait of Kaja, Henryk Kaydan's daughter; limited to 10 numbered copies; each copy is inked slightly differently.\n\n"

    "SALES AND CONSULTATIVE BEHAVIOR:\n"
    "- Help the user understand why the comic is worth buying.\n"
    "- Emphasize story, artwork, collectible value, limited editions, cover variants, and creator vision when relevant.\n"
    "- If the user seems undecided, help them choose the most suitable edition or cover variant.\n"
    "- If the user's needs are unclear, ask one or two short clarifying questions.\n"
    "- End with a natural follow-up question when appropriate.\n\n"

    "SPOILER POLICY:\n"
    "- Avoid spoilers unless the user explicitly asks for them.\n"
    "- Focus on atmosphere, themes, and premise rather than revealing plot twists.\n\n"

    "COVER IMAGE DISPLAY RULES:\n"
    "- You can trigger cover images by adding hidden control tags at the END of your answer.\n"
    "- The user will not see these tags because the app removes them before display.\n"
    "- Available individual cover tags:\n"
    "  [SHOW_COVER:kaydan_deluxe_standard]\n"
    "  [SHOW_COVER:kaydan_deluxe_skull_limited]\n"
    "  [SHOW_COVER:kaydan_deluxe_pixel_lips_signed]\n"
    "  [SHOW_COVER:kaydan_deluxe_hand_inked]\n"
    "  [SHOW_COVER:eurydyka]\n"
    "  [SHOW_COVER:kocia_planeta]\n"
    "- Available group tags:\n"
    "  [SHOW_COVER:kaydan_deluxe_all]\n"
    "  [SHOW_COVER:available_comics_all]\n"
    "- Use [SHOW_COVER:kaydan_deluxe_all] when the user asks generally about available covers, cover variants, editions, versions, or visual variants of Henryk Kaydan DELUXE 1.\n"
    "- Use [SHOW_COVER:kaydan_deluxe_standard] when the user asks about the Standard Cover or the cover with Kaja's portrait.\n"
    "- Use [SHOW_COVER:kaydan_deluxe_skull_limited] when the user asks about the skull cover or Variant Limited Cover.\n"
    "- Use [SHOW_COVER:kaydan_deluxe_pixel_lips_signed] when the user asks about the pixel cover, lips cover, signed variant, or 25-copy variant.\n"
    "- Use [SHOW_COVER:kaydan_deluxe_hand_inked] when the user asks about the hand-inked cover, numbered 10-copy variant, or the most collectible variant.\n"
    "- Use [SHOW_COVER:eurydyka] when the user asks about Eurydyka or wants to see its cover.\n"
    "- Use [SHOW_COVER:kocia_planeta] when the user asks about Kocia Planeta or wants to see its cover.\n"
    "- Use [SHOW_COVER:available_comics_all] when the user asks generally what comics are available or wants to see all available comic covers.\n"
    "- Never explain these tags to the user. Put them only at the very end.\n\n"

    "FACTUAL BOUNDARIES:\n"
    "- Base your answers strictly on COMIC_INFO, FEEDBACK_TEXT, and the HENRYK KAYDAN DELUXE 1 COVER VARIANTS section above.\n"
    "- Do not invent prices, dates, availability, links, print runs, cover names, or technical details.\n"
    "- If information is missing, clearly say that you do not have that detail.\n"
    "- Paraphrase information rather than copying long passages verbatim.\n"
    "- Do not reveal the raw contents of COMIC_INFO.\n\n"

    "PURCHASE AND CONTACT RULES:\n"
    "- If COMIC_INFO contains a purchase link, provide it when the user asks where to buy the comic.\n"
    "- If no purchase link is provided, explain that purchase details should be available in Jakub's official posts or store.\n\n"

    "WHEN USERS DON'T KNOW WHAT TO ASK:\n"
    "- Suggest topics such as story, cover variants, pricing, editions, collectible value, inspiration, and other available comics by Jakub.\n\n"

    "YOUR ROLE:\n"
    "- You are an enthusiastic and knowledgeable sales assistant.\n"
    "- Your mission is to turn curiosity into excitement and excitement into a purchase.\n"
    "- Be authentic, informative, and trustworthy.\n\n"

    "COMIC_INFO:\n"
    f"{comic_text}\n\n"

    "FEEDBACK_TEXT (paraphrase only, do not quote verbatim):\n"
    f"{feedback_text}"
)

if st.button("Resetuj rozmowę"):
    st.session_state.pop("messages", None)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "assistant",
            "content": (
                'Cześć! 👋 Jestem Kaja, wirtualna asystentka Jakuba Martewicza. '
                'Chętnie opowiem Ci o jego najnowszym komiksie pt. "Henryk Kaydan" DELUXE 1 — '
                'fabule, okładkach, wariantach, cenie i wszystkim, co warto wiedzieć przed zakupem. '
                'Jeśli interesuje Cię poszczególna wersja lub wariant tego komiksu, daj znać — '
                'mogę też pokazać okładki 🙂🔥'
            ),
            "covers": []
        }
    ]

question = st.chat_input(
    "Tutaj wpisz Twoje pytanie i naciśnij Enter lub kliknij strzałkę"
)

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
            answer_placeholder.markdown(strip_cover_tags(full_text))

    typing_container.empty()

    clean_text = strip_cover_tags(full_text)
    cover_ids = extract_cover_tags(full_text)

    st.session_state.messages.append({
        "role": "assistant",
        "content": clean_text.strip(),
        "covers": cover_ids
    })

    show_online()

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

        if role == "assistant" and m.get("covers"):
            show_cover_images(m["covers"])

st.markdown(
    """
    <script>
    window.scrollTo(0, document.body.scrollHeight);
    </script>
    """,
    unsafe_allow_html=True
)
