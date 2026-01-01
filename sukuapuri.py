import streamlit as st
import google.generativeai as genai

# --- SIVUN ASETUKSET ---
st.set_page_config(
    page_title="Virtuaalinen Sukututkija",
    page_icon="🕯️",
    layout="centered"
)

# --- CSS-TYYLITTELY (MOSAIIKKI JA VANHA PAPERI) ---
# Tässä luodaan visuaalinen ilme. Taustalla käytetään sekoitusta 
# historiallisista kartoista ja teksteistä (url-linkkeinä).
page_bg_img = """
<style>
/* Koko sovelluksen tausta */
.stApp {
    /* Käytetään taustakuvana historiallista karttaa/käsikirjoitusta */
    background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Karta_öfver_Helsingfors_med_dess_invid_liggande_trakter_1776_-_Kansallisarkisto.jpg/1280px-Karta_öfver_Helsingfors_med_dess_invid_liggande_trakter_1776_-_Kansallisarkisto.jpg");
    background-size: cover;
    background-attachment: fixed;
    background-blend-mode: overlay;
}

/* Luodaan "himmennys" taustakuvan päälle, jotta teksti erottuu */
.stApp::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(255, 250, 240, 0.85); /* Vaalea, kermansävyinen kalvo */
    z-index: -1;
}

/* Otsikoiden tyyli */
h1, h2, h3 {
    font-family: 'Georgia', serif;
    color: #4a3b2a;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
}

/* Chat-viestien tyyli */
.stChatMessage {
    background-color: rgba(255, 255, 255, 0.6);
    border-radius: 15px;
    padding: 10px;
    border: 1px solid #dcd0c0;
}

/* Käyttäjän viesti */
div[data-testid="stChatMessageContent"] {
    font-family: 'Verdana', sans-serif;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# --- 1. API-AVAIMEN HALLINTA ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    with st.sidebar:
        st.header("⚙️ Asetukset")
        api_key = st.text_input("Syötä Google API-avain:", type="password")
        st.info("Hanki avain: aistudio.google.com")

# --- 2. KESKUSTELUHISTORIA ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. KÄYTTÖLIITTYMÄ ---
st.title("🕯️ Virtuaalinen Sukututkija")
st.markdown("""
*Tervetuloa. Olen ohjelmoitu tuntemaan suomalaiset arkistot, kirkonkirjat ja historian käänteet. 
Kysy minulta mitä vain sukututkimukseen liittyvää.*
""")

# Näytetään vanhat viestit
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. TEKOÄLYN LOGIIKKA ---
if api_key:
    genai.configure(api_key=api_key)
    
    # Valitaan malli (käytetään uusinta Flashia, tai Prota jos Flash ei toimi)
    # Tässä on varmistus, joka valitsee automaattisesti toimivan.
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
    except:
        model = genai.GenerativeModel('gemini-pro')

    # Chat-input
    if prompt := st.chat_input("Esim. 'Mitä tarkoittaa itsellinen?' tai 'Miten löydän Karjalan evakot?'"):
        
        # 1. Lisätään käyttäjän viesti historiaan
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Muodostetaan vastaus
        with st.chat_message("assistant"):
            with st.spinner("Tutkitaan arkistoja..."):
                try:
                    # Rakennetaan konteksti (System Prompt)
                    system_instruction = """
                    Olet kokenut, ystävällinen ja perusteellinen suomalainen sukututkija ja historian opettaja.
                    
                    Tehtäväsi on auttaa käyttäjää sukututkimukseen liittyvissä kysymyksissä.
                    - Tunnet suomalaiset lähteet: Kirkonkirjat (rippikirjat, syntyneet, jne.), hen
