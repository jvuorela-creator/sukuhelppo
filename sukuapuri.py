import streamlit as st
import google.generativeai as genai

# --- 1. SIVUN ASETUKSET ---
st.set_page_config(
    page_title="Virtuaalinen Sukututkija",
    page_icon="🕯️",
    layout="wide"
)

# --- 2. TEKOÄLYN OHJEISTUS ---
SYSTEM_PROMPT = """
Olet kokenut, ystävällinen ja perusteellinen suomalainen sukututkija ja historian opettaja.
Tehtäväsi on auttaa käyttäjää sukututkimukseen liittyvissä kysymyksissä.
- Tunnet suomalaiset lähteet: Kirkonkirjat, henkikirjat, tuomiokirjat.
- Tunnet palvelut: HisKi, Kansallisarkiston Astia, SSHY, Finna.
- Osaat selittää vanhoja termejä (esim. "itsellinen", "ruotuvaivainen").
- Vastaa selkeällä suomen kielellä.
"""

# --- 3. TYYLITTELY JA TAUSTAKUVA ---
# Rakennetaan URL osista, jotta se ei katkea kopioidessa
url_part1 = "https://upload.wikimedia.org/wikipedia/commons"
url_part2 = "/0/05/Robert_Wilhelm_Ekman_-_Laukkuryss%C3%A4.jpg"
bg_url = url_part1 + url_part2

# CSS-tyylit
css_styles = f"""
<style>
.stApp {{
    background-image: url("{bg_url}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
.stApp::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(255, 252, 245, 0.85);
    z-index: -1;
}}
h1, h2, h3 {{ font-family: 'Georgia', serif; color: #2c1e12; }}
.stChatMessage {{
    background-color: rgba(255, 255, 255, 0.9);
    border-radius: 10px;
    border: 1px solid #d4c4b0;
}}
section[data-testid="stSidebar"] {{
    background-color: rgba(245, 240, 230, 0.95);
    border-right: 1px solid #d4c4b0;
}}
</style>
"""
st.markdown(css_styles, unsafe_allow_html=True)

# --- 4. API-AVAIMEN TARKISTUS ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.sidebar.error("⚠️ API-avain puuttuu secrets-tiedostosta.")

# --- 5. SIVUPALKKI ---
with st.sidebar:
    st.title("⚙️ Toiminnot")
    st.markdown("---")
    if st.button("🔄 Tyhjennä keskustelu"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.caption("Taustakuva: Robert Wilhelm Ekman, *Laukkuryssä*.")

# --- 6. PÄÄOTSIKKO ---
col1, col2 = st.columns([1, 4])
with col1:
    # Ikoni-URL pätkittynä varmuuden vuoksi
    icon_base = "https://upload.wikimedia.org/wikipedia/commons"
    icon_path = "/thumb/9/9a/Quill_pen_icon.svg/200px-Quill_pen_icon.svg.png"
    st.image(icon_base + icon_path, width=80)
with col2:
    st.title("Virtuaalinen Sukututkija")

st.markdown("*Olen tekoä
