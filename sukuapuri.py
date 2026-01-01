import streamlit as st
import google.generativeai as genai
import random

# --- SIVUN ASETUKSET ---
st.set_page_config(
    page_title="Virtuaalinen Sukututkija",
    page_icon="🕯️",
    layout="wide"
)

# --- OHJEISTUS TEKOÄLYLLE ---
SYSTEM_PROMPT = """
Olet kokenut, ystävällinen ja perusteellinen suomalainen sukututkija ja historian opettaja.
Tehtäväsi on auttaa käyttäjää sukututkimukseen liittyvissä kysymyksissä.
- Tunnet suomalaiset lähteet: Kirkonkirjat, henkikirjat, tuomiokirjat.
- Tunnet palvelut: HisKi, Kansallisarkiston Astia, SSHY, Finna.
- Osaat selittää vanhoja termejä (esim. "itsellinen", "ruotuvaivainen").
- Vastaa selkeällä suomen kielellä.
"""

# --- CSS-TYYLITTELY ---
# Taustakuva (pidetty yhtenäisenä merkkijonona virheiden välttämiseksi)
bg_url = "https://photos.app.goo.gl/cftvvJSzZrwX5jny6"

page_bg_img = f"""
<style>
.stApp {{
    background-image: url("{bg_url}");
    background-size: cover;
    background-attachment: fixed;
    background-blend-mode: overlay;
}}
.stApp::before {{
    content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(250, 245, 235, 0.92); z-index: -1;
}}
h1, h2, h3 {{ font-family: 'Georgia', serif; color: #4a3b2a; text-shadow: 1px 1px 0px #fff; }}
.stChatMessage {{ background-color: #fffaf0; border-radius: 10px; border: 1px solid #dcd0c0; }}
section[data-testid="stSidebar"] {{
    background-color: rgba(245, 240, 230, 0.95);
    border-right: 1px solid #d4c4b0;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# --- KUVA-AARTEET (TURVALLINEN MUOTOILU) ---
# Tässä käytetään "Base URL" -tekniikkaa, jotta rivit pysyvät lyhyinä
# eikä kopiointi aiheuta virheitä.
BASE = "https://upload.wikimedia.org/wikipedia/commons"

kuva_data = [
    ("https://photos.app.goo.gl/FQ5rxzXkvsXGeCGEA"),
    ("https://photos.app.goo.gl/HxNXkxf7XbXMzNuz9"),
    ("https://photos.app.goo.gl/jLjWyN6GKNvE5qpF6"),
    ("https://photos.app.goo.gl/nRtXVsFF4pmDAD1L6"),
    ("https://photos.app.goo.gl/EfY9zKKmby3TdBQr7"),
    ("https://photos.app.goo.gl/TmCAcKfMeeWWGJgU6"),
    ("https://photos.app.goo.gl/ZavRwPw1CJEHCaCv8")
]

# --- 1. API-AVAIMEN HAKU ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    # Jos avainta ei ole, näytetään virhe mutta ei kaadeta koko sovellusta heti
    st.sidebar.error("API-avain puuttuu.")

# --- 2. SIVUPALKKI ---
with st.sidebar:
    st.title("📜 Arkiston kätköistä")
    st.markdown("---")
    
    # Rakennetaan kuvat turvallisesti
    try:
        valinnat = random.sample(kuva_data, 2)
        for polku, teksti in valinnat:
            # Yhdistetään alkuosa ja loppuosa tässä
            koko_url = BASE + polku
            st.image(koko_url, caption=teksti, use_column_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
    except Exception:
        st.write("Kuvia ei voitu ladata.")

    st.markdown("---")
    if st.button("🔄 Tyhjennä keskustelu"):
        st.session_state.messages = []
        st.rerun()

# --- 3. PÄÄNÄKYMÄ ---
col1, col2 = st.columns([1, 4])
with col1:
    # Lyhyt ikoni-osoite, ei pitäisi katketa
    icon_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Quill_pen_icon.svg/200px-Quill_pen_icon.svg.png"
    st.image(icon_url, width=80)
with col2:
    st.title("Virtuaalinen Sukututkija")

st.markdown("""
*Tervetuloa menneisyyden jäljille. Olen tekoälyavustajasi, joka tuntee suomalaiset arkistot 
ja historian käänteet.*
""")

# --- 4. CHAT-LOGIIKKA ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def hae_toimiva_malli():
    if not api_key: return None
    try:
        genai.configure(api_key=api_key)
        all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        toiveet = ["models/gemini-1.5-flash", "models/gemini-pro", "models/gemini-1.0-pro"]
        for toive in toiveet:
            if toive in all_models: return genai.GenerativeModel(toive)
        if all_models: return genai.GenerativeModel(all_models[0])
    except:
        return genai.GenerativeModel("gemini-pro")
    return None

if prompt := st.chat_input("Kysy esimerkiksi: 'Mitä tarkoittaa itsellinen?'"):
    if not api_key:
        st.error("API-avain puuttuu. Lisää se Secrets-tiedostoon.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Selaillaan vanhoja asiakirjoja..."):
                try:
                    model = hae_toimiva_malli()
                    if model:
                        full_prompt = f"{SYSTEM_PROMPT}\n\nKäyttäjän kysymys: {prompt}"
                        response = model.generate_content(full_prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    else:
                        st.error("Virhe: Tekoälymallia ei saatu käyttöön.")
                except Exception as e:
                    st.error("Palvelussa on ruuhkaa. Kokeile hetken kuluttua uudelleen.")

