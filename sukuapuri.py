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

# --- CSS-TYYLITTELY (TAUSTAKUVA) ---
# Käytetään Robert Wilhelm Ekmanin "Laukkuryssä"-teosta taustana.
bg_url = "https://upload.wikimedia.org/wikipedia/commons/0/05/Robert_Wilhelm_Ekman_-_Laukkuryss%C3%A4.jpg"

page_bg_img = f"""
<style>
/* Koko sovelluksen tausta */
.stApp {{
    background-image: url("{bg_url}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

/* Himmennyskalvo taustakuvan päälle */
.stApp::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(255, 252, 245, 0.85); 
    z-index: -1;
}}

/* Tekstien tyylit */
h1, h2, h3 {{ font-family: 'Georgia', serif; color: #2c1e12; }}
p, div {{ color: #2c1e12; }}

/* Chat-viestien laatikot */
.stChatMessage {{ 
    background-color: rgba(255, 255, 255, 0.85);
    border-radius: 10px; 
    border: 1px solid #d4c4b0; 
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
    st.sidebar.error("⚠️ API-avain puuttuu.")

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
    # Ikoni
    st.markdown('<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Quill_pen_icon.svg/200px-Quill_pen_icon.svg.png" width="80">', unsafe_allow_html=True)
with col2:
    st.title("Virtuaalinen Sukututkija")

st.markdown("""
*Tervetuloa menneisyyden jäljille. Olen tekoälyavustaj
