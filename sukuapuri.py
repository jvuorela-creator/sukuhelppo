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

# --- CSS-TYYLITTELY (UUSI TAUSTAKUVA) ---
# Käytetään haluttua kuvaa taustana.
# URL on koodattu turvallisesti (URL-enkoodattu 'ä' -> '%C3%A4'), jotta se toimii varmasti.
bg_url = "https://upload.wikimedia.org/wikipedia/commons/0/05/Robert_Wilhelm_Ekman_-_Laukkuryss%C3%A4.jpg"

page_bg_img = f"""
<style>
/* Koko sovelluksen tausta */
.stApp {{
    background-image: url("{bg_url}");
    background-size: cover;       /* Kuva peittää koko ruudun */
    background-position: center;  /* Kuva keskitetään */
    background-attachment: fixed; /* Kuva pysyy paikallaan skrollatessa */
}}

/* Himmennyskalvo taustakuvan päälle, jotta teksti erottuu paremmin */
.stApp::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    /* Vaalea, hieman läpinäkyvä kerros kuvan päällä */
    background-color: rgba(255, 252, 245, 0.85); 
    z-index: -1;
}}

/* Otsikoiden ja tekstien tyylit */
h1, h2, h3 {{ font-family: 'Georgia', serif; color: #2c1e12; text-shadow: 1px 1px 0px rgba(255,255,255,0.5); }}
p, div {{ color: #2c1e12; }}

/* Chat-viestien laatikot */
.stChatMessage {{ 
    background-color: rgba(255, 255, 255, 0.8); /* Hieman läpinäkyvä tausta */
    border-radius: 10px; 
    border: 1px solid #d4c4b0; 
    box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
}}

/* Sivupalkin tyyli */
section[data-testid="stSidebar"] {{
    background-color: rgba(245, 240, 230, 0.95);
    border-right: 1px solid #d4c4b0;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# --- 1. API-AVAIMEN HAKU ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    # Näytetään virhe sivupalkissa, jos avain puuttuu
    st.sidebar.error("⚠️ API-avain puuttuu secrets-tiedostosta. Lisää se Streamlitin hallintapaneelista.")

# --- 2. SIVUPALKKI ---
with st.sidebar:
    st.title("⚙️ Toiminnot")
    st.markdown("---")
    if st.button("🔄 Tyhjennä keskustelu"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.caption("Taustakuva: Robert Wilhelm Ekman, *Laukkuryssä*.")

# --- 3. PÄÄNÄKYMÄ ---
col1, col2 = st.columns([1, 4])
with col1:
    # Ikoni (käytetään HTMLää varmuuden vuoksi)
    st.markdown('<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Quill_pen_icon.svg/200px-Quill_pen_icon.svg.png" width="80">', unsafe_allow_html=True)
with col2:
    st.title("Virtuaalinen Sukututkija")

st.markdown("""
*Tervetuloa menneisyyden jäljille. Olen tekoälyavustajasi, joka tuntee suomalaiset arkistot 
ja historian käänteet.*
""")

# --- 4. CHAT-LOGIIKKA ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tulostetaan vanhat viestit
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Mallin haku -funktio
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
        # Hätätapauksessa kokeillaan vanhinta mallia
        return genai.GenerativeModel("gemini-pro")
    return None

# Kysymyskenttä ja vastauslogiikka
if prompt := st.chat_input("Kysy esimerkiksi: 'Mitä tarkoittaa itsellinen?'"):
    if not api_key:
        st.error("API-avain puuttuu. Palvelu ei voi vastata.")
    else:
        # Käyttäjän viesti
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Tekoälyn vastaus
        with st.chat_message("assistant"):
            with st.spinner("Selaillaan vanhoja asiakirjoja..."):
                try:
                    model = hae_toimiva_malli()
                    if model:
                        full_prompt = f"{SYSTEM_PROMPT}\n\nKäyttä
