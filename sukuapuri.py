import streamlit as st
import google.generativeai as genai

# --- 1. SIVUN ASETUKSET ---
st.set_page_config(
    page_title="Virtuaalinen Sukututkija",
    page_icon="🕯️",
    layout="wide"
)

# --- 2. TEKOÄLYN OHJEISTUS ---
# Käytetään sulkuja tekstin jakamiseen usealle riville turvallisesti
SYSTEM_PROMPT = (
    "Olet kokenut, ystävällinen ja perusteellinen "
    "suomalainen sukututkija ja historian opettaja.\n"
    "Tehtäväsi on auttaa käyttäjää sukututkimukseen liittyvissä kysymyksissä.\n"
    "- Tunnet suomalaiset lähteet: Kirkonkirjat, henkikirjat, tuomiokirjat.\n"
    "- Tunnet palvelut: HisKi, Kansallisarkiston Astia, SSHY, Finna.\n"
    "- Osaat selittää vanhoja termejä (esim. 'itsellinen', 'ruotuvaivainen').\n"
    "- Vastaa selkeällä suomen kielellä."
)

# --- 3. TYYLITTELY JA TAUSTAKUVA ---
# Rakennetaan URL paloista virheiden välttämiseksi
url_root = "https://upload.wikimedia.org/wikipedia/commons"
url_img = "/0/05/Robert_Wilhelm_Ekman_-_Laukkuryss%C3%A4.jpg"
bg_url = url_root + url_img

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
    st.caption("(c) SUKU -lehti 2026")

# --- 6. PÄÄOTSIKKO ---
col1, col2 = st.columns([1, 4])
with col1:
    # Ikoni rakennettu paloista
    icon_root = "https://upload.wikimedia.org/wikipedia/commons"
    icon_file = "/thumb/9/9a/Quill_pen_icon.svg/200px-Quill_pen_icon.svg.png"
    st.image(icon_root + icon_file, width=80)
with col2:
    st.title("Virtuaalinen Sukututkija")

# TÄMÄ RIVI AIHEUTTI VIRHEEN AIEMMIN - NYT KORJATTU:
welcome_text = (
    "*Olen tekoälyavustajasi. "
    "Kysy minulta arkistoista, termeistä tai historiasta.*"
)
st.markdown(welcome_text)

# --- 7. CHAT-LOGIIKKA ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Näytä vanhat viestit
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Funktio mallin valintaan
def hae_malli():
    if not api_key: return None
    try:
        genai.configure(api_key=api_key)
        # Haetaan mallit
        models = [m.name for m in genai.list_models()]
        # Suodatetaan
        capable_models = []
        for m in models:
             if 'generateContent' in genai.get_model(m).supported_generation_methods:
                 capable_models.append(m)

        priority = [
            "models/gemini-1.5-flash", 
            "models/gemini-pro", 
            "models/gemini-1.0-pro"
        ]
        
        for p in priority:
            if p in capable_models: return genai.GenerativeModel(p)
            
        if capable_models: return genai.GenerativeModel(capable_models[0])
        
    except:
        pass
    return genai.GenerativeModel("gemini-pro")

# Käyttäjän syöte
prompt = st.chat_input("Kirjoita kysymyksesi tähän...")

if prompt:
    if not api_key:
        st.error("API-avain puuttuu.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Tutkitaan lähteitä..."):
                try:
                    model = hae_malli()
                    if model:
                        # Yhdistetään tekstit turvallisesti
                        final_prompt = (
                            SYSTEM_PROMPT + 
                            "\n\nKäyttäjän kysymys: " + 
                            prompt
                        )
                        
                        response = model.generate_content(final_prompt)
                        st.markdown(response.text)
                        
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response.text
                        })
                    else:
                        st.error("Virhe: Tekoälymallia ei saatu käyttöön.")
                except Exception as e:
                    st.error("Hetkellinen häiriö. Kokeile uudelleen.")

