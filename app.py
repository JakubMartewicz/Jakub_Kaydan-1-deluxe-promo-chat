import os
import re
import time
import base64

import streamlit as st
from openai import OpenAI


st.set_page_config(
    page_title="Komiksy Jakuba Martewicza",
    page_icon="💬"
)

BUY_LINK = "https://allegrolokalnie.pl/uzytkownik/rufur3"


def image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def set_bg(image_path: str):
    try:
        data = image_to_base64(image_path)

        st.markdown(f"""
        <style>
        html, body {{
            background: #000 !important;
        }}

        .stApp {{
            background-color: #000 !important;
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
                rgba(0, 0, 0, 0.35) 0%,
                rgba(0, 0, 0, 0.50) 40%,
                rgba(0, 0, 0, 0.65) 100%
            );
            z-index: 0;
            pointer-events: none;
        }}

        .main,
        header,
        footer,
        [data-testid="stSidebar"] {{
            position: relative;
            z-index: 1;
        }}

        .buy-now-button {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 15px 34px;
            margin: 10px 0 22px 0;
            border-radius: 999px;
            overflow: hidden;
            white-space: nowrap;
            cursor: pointer;
            outline: none !important;
            -webkit-tap-highlight-color: transparent;

            background:
                linear-gradient(
                    180deg,
                    rgba(255,255,255,0.14) 0%,
                    rgba(255,255,255,0.02) 100%
                ),
                linear-gradient(
                    135deg,
                    #5a0505 0%,
                    #8b0d0d 22%,
                    #c1121f 55%,
                    #e85d04 82%,
                    #ffb703 100%
                );

            color: #ffffff !important;
            font-weight: 800;
            font-size: 18px;
            text-decoration: none !important;
            letter-spacing: 0.45px;

            border: 1px solid rgba(255, 220, 160, 0.22);

            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.16),
                inset 0 -1px 0 rgba(0,0,0,0.25),
                0 10px 24px rgba(80, 0, 0, 0.45),
                0 4px 14px rgba(255, 122, 0, 0.22);

            text-shadow:
                0 1px 2px rgba(0,0,0,0.35),
                0 0 8px rgba(255,255,255,0.08);

            transition:
                transform 0.22s ease,
                box-shadow 0.22s ease,
                filter 0.22s ease;

            transform: translateY(0);
            backdrop-filter: blur(6px);
            -webkit-backdrop-filter: blur(6px);
        }}

        .buy-now-button:visited,
        .buy-now-button:link {{
            color: #ffffff !important;
            text-decoration: none !important;
        }}

        .buy-now-button:hover {{
            transform: translateY(-3px) scale(1.02);
            color: #ffffff !important;
            filter: brightness(1.08);

            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.18),
                inset 0 -1px 0 rgba(0,0,0,0.25),
                0 16px 34px rgba(80, 0, 0, 0.55),
                0 8px 18px rgba(255, 122, 0, 0.30);
        }}

        .buy-now-button:active {{
            transform: translateY(1px) scale(0.99);
        }}

        .buy-now-button:focus,
        .buy-now-button:focus-visible {{
            outline: none !important;
        }}
        </style>
        """, unsafe_allow_html=True)

    except FileNotFoundError:
        st.warning(f"Brakuje pliku tła: {image_path}")


def show_intro_animation(face_path: str, skull_path: str):
    try:
        face_data = image_to_base64(face_path)
        skull_data = image_to_base64(skull_path)

        st.markdown(f"""
        <style>
        .kaja-intro {{
            position: fixed;
            inset: 0;
            z-index: 2147483647;
            background: #000;
            display: flex;
            align-items: center;
            justify-content: center;
            pointer-events: none;
            animation: introFadeOut 0.35s ease forwards;
            animation-delay: 1.65s;
        }}

        .kaja-intro-inner {{
            position: relative;
            width: min(78vw, 560px);
            height: min(84vh, 780px);
        }}

        .kaja-intro-inner::after {{
            content: "";
            position: absolute;
            inset: -10%;
            pointer-events: none;
            background: radial-gradient(
                circle at center,
                rgba(0,0,0,0) 42%,
                rgba(0,0,0,0.18) 58%,
                rgba(0,0,0,0.55) 74%,
                rgba(0,0,0,0.88) 88%,
                rgba(0,0,0,1) 100%
            );
        }}

        .kaja-intro-img {{
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
            object-fit: contain;

            -webkit-mask-image: radial-gradient(
                circle at center,
                rgba(0,0,0,1) 0%,
                rgba(0,0,0,1) 56%,
                rgba(0,0,0,0.95) 68%,
                rgba(0,0,0,0.65) 82%,
                rgba(0,0,0,0) 100%
            );

            mask-image: radial-gradient(
                circle at center,
                rgba(0,0,0,1) 0%,
                rgba(0,0,0,1) 56%,
                rgba(0,0,0,0.95) 68%,
                rgba(0,0,0,0.65) 82%,
                rgba(0,0,0,0) 100%
            );
        }}

        .kaja-face {{
            opacity: 1;
            transform: scale(1.02);
            animation: faceToSkull 1.45s ease-in-out forwards;
        }}

        .kaja-skull {{
            opacity: 0;
            transform: scale(1.08);
            animation: skullAppearAndFade 1.90s ease-in-out forwards;
        }}

        @keyframes faceToSkull {{
            0% {{
                opacity: 1;
                transform: scale(1.02);
                filter: blur(0px) brightness(1);
            }}
            45% {{
                opacity: 0.65;
                transform: scale(1.04);
                filter: blur(1px) brightness(0.8);
            }}
            100% {{
                opacity: 0;
                transform: scale(1.08);
                filter: blur(4px) brightness(0.25);
            }}
        }}

        @keyframes skullAppearAndFade {{
            0% {{
                opacity: 0;
                transform: scale(1.08);
                filter: blur(4px) brightness(0.7);
            }}
            35% {{
                opacity: 0.75;
                transform: scale(1.05);
                filter: blur(1px) brightness(0.85);
            }}
            65% {{
                opacity: 1;
                transform: scale(1.02);
                filter: blur(0px) brightness(0.9);
            }}
            100% {{
                opacity: 0;
                transform: scale(1.00);
                filter: blur(5px) brightness(0.03);
            }}
        }}

        @keyframes introFadeOut {{
            0% {{
                opacity: 1;
                visibility: visible;
            }}
            99% {{
                opacity: 0;
                visibility: visible;
            }}
            100% {{
                opacity: 0;
                visibility: hidden;
                z-index: -1;
            }}
        }}
        </style>

        <div class="kaja-intro">
            <div class="kaja-intro-inner">
                <img class="kaja-intro-img kaja-face" src="data:image/png;base64,{face_data}">
                <img class="kaja-intro-img kaja-skull" src="data:image/png;base64,{skull_data}">
            </div>
        </div>
        """, unsafe_allow_html=True)

    except FileNotFoundError:
        pass


def get_secret(name: str, default: str = ""):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


def last_messages(messages, n=12):
    system = [messages[0]]
    tail = messages[1:][-n:]
    return system + tail


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


SAMPLE_PAGES = {
    "sample_page_1": {
        "label": "Przykładowa plansza 1",
        "path": "assets/pages/sample_page_1.png",
    },
    "sample_page_2": {
        "label": "Przykładowa plansza 2",
        "path": "assets/pages/sample_page_2.png",
    },
    "sample_page_3": {
        "label": "Przykładowa plansza 3",
        "path": "assets/pages/sample_page_3.png",
    },
    "sample_page_4": {
        "label": "Przykładowa plansza 4",
        "path": "assets/pages/sample_page_4.png",
    },
}


SAMPLE_PAGE_GROUPS = {
    "sample_pages_all": [
        "sample_page_1",
        "sample_page_2",
        "sample_page_3",
        "sample_page_4",
    ]
}


def strip_control_tags(text: str) -> str:
    text = text or ""
    text = re.sub(r"\[SHOW_COVER:[a-zA-Z0-9_,\- ]+\]", "", text)
    text = re.sub(r"\[SHOW_PAGE:[a-zA-Z0-9_,\- ]+\]", "", text)
    return text.strip()


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


def extract_page_tags(text: str):
    tags = re.findall(r"\[SHOW_PAGE:([a-zA-Z0-9_,\- ]+)\]", text or "")
    page_ids = []

    for tag in tags:
        parts = [x.strip() for x in tag.split(",") if x.strip()]

        for part in parts:
            if part in SAMPLE_PAGE_GROUPS:
                page_ids.extend(SAMPLE_PAGE_GROUPS[part])
            elif part in SAMPLE_PAGES:
                page_ids.append(part)

    return list(dict.fromkeys(page_ids))


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


def show_sample_pages(page_ids):
    if not page_ids:
        return

    for page_id in page_ids:
        page = SAMPLE_PAGES.get(page_id)

        if not page:
            continue

        if os.path.exists(page["path"]):
            st.image(
                page["path"],
                caption=page["label"],
                use_container_width=True
            )
        else:
            st.caption(f"⚠️ Brakuje pliku planszy: {page['path']}")


set_bg("assets/backgroundpic.png")

if "intro_seen" not in st.session_state:
    show_intro_animation(
        "assets/intro/kaja_face.png",
        "assets/intro/kaja_skull.png"
    )
    st.session_state.intro_seen = True


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


st.markdown(f"""
<a href="{BUY_LINK}" target="_blank" rel="noopener noreferrer" class="buy-now-button">
    <span>🛒</span>
    <span>Kup teraz</span>
</a>
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
    "- Emphasize story, artwork, collectible value, limited editions, cover variants, sample pages, and creator vision when relevant.\n"
    "- If the user seems undecided, help them choose the most suitable edition or cover variant.\n"
    "- If useful, offer to show cover variants or sample pages.\n"
    "- If the user's needs are unclear, ask one or two short clarifying questions.\n"
    "- End with a natural follow-up question when appropriate.\n\n"

    "SPOILER POLICY:\n"
    "- Avoid spoilers unless the user explicitly asks for them.\n"
    "- Focus on atmosphere, themes, artwork, and premise rather than revealing plot twists.\n\n"

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

    "SAMPLE PAGE DISPLAY RULES:\n"
    "- You can trigger sample comic pages by adding hidden control tags at the END of your answer.\n"
    "- The user will not see these tags because the app removes them before display.\n"
    "- Available sample page tags:\n"
    "  [SHOW_PAGE:sample_page_1]\n"
    "  [SHOW_PAGE:sample_page_2]\n"
    "  [SHOW_PAGE:sample_page_3]\n"
    "  [SHOW_PAGE:sample_page_4]\n"
    "- Available group tag:\n"
    "  [SHOW_PAGE:sample_pages_all]\n"
    "- When the user asks for sample pages, preview pages, example pages, interior art, inside pages, fragments, or how the comic looks inside, use [SHOW_PAGE:sample_pages_all].\n"
    "- By default, show sample pages in this order: sample_page_1, sample_page_2, sample_page_3, sample_page_4.\n"
    "- If the user asks for a specific sample page number, show only that page.\n"
    "- If the user asks to see another page, next page, more pages, or all sample pages, use [SHOW_PAGE:sample_pages_all].\n"
    "- If the user asks which sample page is best, most interesting, strongest, nicest, most atmospheric, or asks for your recommendation, choose sample_page_1 as the default recommended page unless COMIC_INFO clearly supports another choice.\n"
    "- When recommending the best sample page, briefly explain that it is your recommended preview and include [SHOW_PAGE:sample_page_1].\n"
    "- If the user asks to compare or decide between sample pages after seeing them, answer with one recommendation and show that page again using the appropriate [SHOW_PAGE:...] tag.\n"
    "- If you say that you are showing sample pages, you MUST include the appropriate [SHOW_PAGE:...] tag in the same response.\n"
    "- Never promise to show sample pages without including the required tag.\n"
    "- Never answer a question about the best sample page without either showing one page or clearly asking whether the user wants to see it.\n"
    "- Proactively offer sample pages when the user is undecided, asks whether the comic is worth buying, asks about the artwork, drawing style, atmosphere, or wants to see what is inside.\n"
    "- Do not overuse sample pages in every answer. Use them when they genuinely help the user decide or understand the comic.\n"
    "- Never explain these tags to the user. Put them only at the very end.\n\n"

    "SALES PSYCHOLOGY:\n"
    "- Use social proof, emotional selling, scarcity, and consultative recommendations naturally.\n"
    "- Help the user feel the atmosphere and collectible value of the comic.\n"
    "- When helpful, proactively offer cover variants or sample pages.\n"
    "- If the user shows strong interest, confidently encourage them to use the 'Kup teraz' button.\n"
    "- Keep the tone warm, engaging, and non-pushy.\n\n"

    "ARTISTIC CRAFTSMANSHIP:\n"
    "- Naturally emphasize that Jakub Martewicz creates his comics entirely by hand using traditional techniques such as pencil and ink.\n"
    "- Clearly communicate that no AI is used to create the comic artwork.\n"
    "- Highlight that each page is the result of genuine craftsmanship, patience, and artistic dedication.\n"
    "- When relevant, mention that Jakub's creative process follows the tradition of classic comic masters.\n"
    "- Present the comic as authentic, handcrafted art rather than mass-produced digital content.\n"
    "- Emphasize that each issue is an expression of Jakub's lifelong passion for comics.\n"
    "- Use this angle naturally when discussing artwork quality, originality, atmosphere, or collectible value.\n\n"

    "COMMUNITY AND CONTENT:\n"
    "- When appropriate, mention that fans can follow Jakub's work through his YouTube channel 'Komiksowa Nawijka'.\n"
    "- The YouTube channel link is provided in the YOUTUBE_LINK secret.\n"
    "- The Facebook group 'Jakub Martewicz Art' is a place where readers can ask questions, follow updates, and connect with the community.\n"
    "- Mention these channels naturally as part of a friendly recommendation, not as aggressive promotion.\n\n"

    "CONVERSATION CLOSING RULES:\n"
    "- If the user clearly ends the conversation (e.g. says 'dziękuję', 'dzięki', 'na razie', 'do zobaczenia', 'to wszystko'), end with a warm farewell.\n"
    "- In that farewell, you may naturally mention:\n"
    "  - the 'Kup teraz' button,\n"
    "  - the Facebook group 'Jakub Martewicz Art',\n"
    "  - the Instagram profile,\n"
    "  - the YouTube channel 'Komiksowa Nawijka' using the YOUTUBE_LINK secret.\n"
    "- Keep this closing concise, elegant, and non-pushy.\n"
    "- If the user continues the conversation after such a farewell, do NOT repeat these links in every subsequent response.\n"
    "- Only mention the links again later if the user explicitly asks for them or if they become genuinely relevant.\n\n"

    "SOCIAL PROOF:\n"
    "- When relevant, use FEEDBACK_TEXT to highlight positive reader reactions.\n"
    "- Paraphrase feedback rather than quoting it verbatim.\n\n"

    "CALL TO ACTION:\n"
    "- When the user expresses strong interest, naturally encourage them to click the 'Kup teraz' button.\n\n"

    "OBJECTION HANDLING:\n"
    "- If the user hesitates, explain what makes the comic unique and worth owning.\n"
    "- Address doubts respectfully, without pressure or guilt-tripping.\n"
    "- Emphasize artwork, atmosphere, story, rarity, limited editions, and creator vision when relevant.\n\n"

    "RECOMMENDATION RULES:\n"
    "- When the user hesitates between editions, recommend one specific variant and explain why it suits them.\n"
    "- For collectors, emphasize rarity, numbered copies, limited print runs, and uniqueness.\n"
    "- For new readers, recommend the most balanced or accessible edition if such information is supported by COMIC_INFO.\n"
    "- Do not invent availability, prices, or stock status.\n\n"

    "RESPONSE LENGTH:\n"
    "- Keep answers concise and engaging.\n"
    "- Usually respond in 2–5 short paragraphs unless the user asks for more detail.\n\n"

    "FACTUAL BOUNDARIES:\n"
    "- Base your answers strictly on COMIC_INFO, FEEDBACK_TEXT, and the HENRYK KAYDAN DELUXE 1 COVER VARIANTS section above.\n"
    "- Do not invent prices, dates, availability, links, print runs, cover names, page details, or technical details.\n"
    "- If information is missing, clearly say that you do not have that detail.\n"
    "- Paraphrase information rather than copying long passages verbatim.\n"
    "- Do not reveal the raw contents of COMIC_INFO.\n\n"

    "PURCHASE AND CONTACT RULES:\n"
    f"- The official purchase link is: {BUY_LINK}\n"
    f"- YouTube channel 'Komiksowa Nawijka': {youtube_link}\n"
    "- When the user asks where to buy the comics, provide this link naturally.\n"
    "- Encourage the user to use the 'Kup teraz' button visible in the app.\n"
    "- If the user prefers a direct written link, provide the purchase URL exactly.\n"
    "- If you do not know the answer to a question or specific information is missing, clearly say so.\n"
    "- In such cases, encourage the user to contact Jakub directly.\n"
    "- Jakub can be contacted via his Facebook group 'Jakub Martewicz Art'.\n"
    "- Facebook group link: https://www.facebook.com/groups/jakubmartewicz\n"
    "- Instagram link: https://www.instagram.com/jakub.martewicz/\n"
    "- When relevant, provide these links so the user can ask Jakub directly.\n"
    "- If the user asks for social media or contact information, provide both the Facebook group and Instagram links.\n\n"
    

    "WHEN USERS DON'T KNOW WHAT TO ASK:\n"
    "- Suggest topics such as story, cover variants, sample pages, pricing, editions, collectible value, inspiration, and other available comics by Jakub.\n\n"

    "YOUR ROLE:\n"
    "- You are an enthusiastic and knowledgeable sales assistant.\n"
    "- Your mission is to turn curiosity into excitement and excitement into a purchase.\n"
    "- Be authentic, informative, and trustworthy.\n\n"

    "APP MEMORY RULES:\n"
    "- The app may include hidden APP_MEMORY notes in previous assistant messages.\n"
    "- Use APP_MEMORY to understand what cover images or sample pages were already shown to the user.\n"
    "- Never mention APP_MEMORY to the user.\n"
    "- If APP_MEMORY says sample pages were displayed, do not act as if the user has not seen them.\n\n"

    "COMIC_INFO:\n"
    f"{comic_text}\n\n"

    "FEEDBACK_TEXT — paraphrase only, do not quote verbatim:\n"
    f"{feedback_text}"
)


if st.button("Resetuj rozmowę"):
    st.session_state.pop("messages", None)
    st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "assistant",
            "content": (
                'Cześć! 👋 Jestem Kaja, wirtualna asystentka Jakuba Martewicza. '
                'Chętnie opowiem Ci o jego najnowszym komiksie pt. "Henryk Kaydan" DELUXE 1 — '
                'mogę też pokazać okładki lub przykładowe plansze 🙂🔥'
            ),
            "covers": [],
            "pages": []
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
            answer_placeholder.markdown(strip_control_tags(full_text))

    typing_container.empty()

    clean_text = strip_control_tags(full_text)
    cover_ids = extract_cover_tags(full_text)
    page_ids = extract_page_tags(full_text)

    memory_note = ""

    if cover_ids:
        memory_note += f"\n\n[APP_MEMORY: In this response, the app displayed cover images: {', '.join(cover_ids)}.]"

    if page_ids:
        memory_note += f"\n\n[APP_MEMORY: In this response, the app displayed sample pages: {', '.join(page_ids)}.]"

    st.session_state.messages.append({
        "role": "assistant",
        "content": clean_text.strip() + memory_note,
        "display_content": clean_text.strip(),
        "covers": cover_ids,
        "pages": page_ids
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
        st.markdown(m.get("display_content", m["content"]))

        if role == "assistant" and m.get("covers"):
            show_cover_images(m["covers"])

        if role == "assistant" and m.get("pages"):
            show_sample_pages(m["pages"])


st.markdown(
    """
    <script>
    window.scrollTo(0, document.body.scrollHeight);
    </script>
    """,
    unsafe_allow_html=True
)
