import streamlit as st
import google.generativeai as genai

# --- SIVUN ASETUKSET ---
st.set_page_config(
    page_title="Virtuaalinen Sukututkija",
    page_icon="🕯️",
    layout="centered"
)

# --- OHJEISTUS TEKOÄLYLLE (Tämä on se kohta, jossa virhe oli) ---
# Määritellään ohjeistus tässä alussa, jotta koodi pysyy siistinä.
SYSTEM_PROMPT = """
Olet kokenut, ystävällinen ja perusteellinen suomalainen sukututkija ja historian opettaja.

Tehtäväsi on auttaa käyttäjää sukututkimukseen liittyvissä kysymyksissä.
- Tunnet suomalaiset lähteet: Kirkonkirjat (rippikirjat, syntyneet, jne.), henkikirjat, tuomiokirjat.
- Tunnet palvelut: HisKi, Kansallisarkiston Astia, SSHY:n kuvatietokanta, Finna.
- Osaat selittää vanhoja termejä, ammatteja ja sairauksia (esim. "itsellinen", "ruotuvaivainen", "punatauti").
- Vastaa selkeällä suomen kielellä. Jos kysymys on monitulkintainen, tarjoa vaihtoehtoja.
- Käytä vastauksissa tarvittaessa luetteloita ja selkeitä kappaleita.
"""

# --- CSS-TYYLITTELY (MOSAIIKKI JA VANHA PAPERI) ---
page_bg_img = """
<style>
/* Koko sovelluksen tausta */
.stApp {
    background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Karta_öfver_Helsingfors_med_dess_invid_liggande_trakter_1776_-_Kansallisarkisto.jpg/1280px-Karta_öfver_Helsingfors_med_dess_invid_liggande_trakter_1776_-_Kansallisarkisto.jpg");
    background-size: cover;
    background-attachment: fixed;
    background-blend-mode: overlay;
}
.stApp::before {
    content: "";
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(255, 250, 240, 0.90); /* Hieman peittävämpi tausta luettavuuden vuoksi */
    z-index: -1;
}
h1, h2, h3 { font-family: 'Georgia', serif; color: #4a3b2a; }
.stChatMessage { background-color: rgba(255, 255, 255, 0.7); border-radius: 10px; border: 1px solid #dcd0c0; }
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

# --- 2. KESKUSTELUHISTORIA ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. KÄYTTÖLIITTYMÄ ---
st.title("🕯️ Virtuaalinen Sukututkija")
st.markdown("Kysy minulta vanhoista termeistä, lähteistä tai tutkimusongelmista.")

# Näytetään vanhat viestit
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. TEKOÄLYN LOGIIKKA ---
if api_key:
    genai.configure(api_key=api_key)
    
    # Valitaan malli automaattisesti
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
    except:
        model = genai.GenerativeModel('gemini-pro')

    # Chat-input
    if prompt := st.chat_input("Kirjoita kysymyksesi tähän..."):
        
        # 1. Lisätään käyttäjän viesti historiaan
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Muodostetaan vastaus
        with st.chat_message("assistant"):
            with st.spinner("Tutkitaan arkistoja..."):
                try:
                    # Aloitetaan uusi chat-sessio (ilman historiaa tässä kohtaa, jotta SYSTEM_PROMPT menee perille)
                    # Huom: Oikeassa keskustelussa historiaa pitäisi hallita tarkemmin, 
                    # mutta tässä versiossa yksinkertaistamme lähettämällä ohjeen joka kerta.
                    
                    full_prompt = f"{SYSTEM_PROMPT}\n\nKäyttäjän kysymys: {prompt}"
                    
                    response = model.generate_content(full_prompt)
                    
                    st.markdown(response.text)
                    
                    # Tallennetaan vastaus historiaan
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                except Exception as e:
                    st.error(f"Tapahtui virhe: {e}")
else:
    if not api_key:
        st.warning("Syötä API-avain sivupalkkiin aloittaaksesi.")

# Tyhjennysnappi sivupalkkiin
with st.sidebar:
    if st.button("Aloita uusi keskustelu"):
        st.session_state.messages = []
        st.rerun()
