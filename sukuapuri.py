import streamlit as st
import google.generativeai as genai

# --- SIVUN ASETUKSET ---
st.set_page_config(
    page_title="Virtuaalinen Sukututkija",
    page_icon="🕯️",
    layout="centered"
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
page_bg_img = """
<style>
.stApp {
    background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Karta_öfver_Helsingfors_med_dess_invid_liggande_trakter_1776_-_Kansallisarkisto.jpg/1280px-Karta_öfver_Helsingfors_med_dess_invid_liggande_trakter_1776_-_Kansallisarkisto.jpg");
    background-size: cover;
    background-attachment: fixed;
    background-blend-mode: overlay;
}
.stApp::before {
    content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(255, 250, 240, 0.90); z-index: -1;
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

# --- 3. APUFUKTIO: ETSI TOIMIVA MALLI (RATKAISU ONGELMAAN) ---
def hae_toimiva_malli():
    """Etsii listasta mallin, joka on varmasti olemassa."""
    try:
        # Haetaan kaikki mallit, jotka tukevat tekstin tuottamista
        all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Tulostetaan löydetyt mallit sivupalkkiin debuggausta varten (voit poistaa myöhemmin)
        # st.sidebar.write("Löydetyt mallit:", all_models)

        # Ensisijaiset toiveet järjestyksessä
        toiveet = ["models/gemini-1.5-flash", "models/gemini-pro", "models/gemini-1.0-pro"]
        
        for toive in toiveet:
            if toive in all_models:
                return genai.GenerativeModel(toive)
        
        # Jos toiveita ei löydy, otetaan listan ensimmäinen toimiva
        if all_models:
            return genai.GenerativeModel(all_models[0])
            
    except Exception as e:
        # Hätätapaus: Jos listauskaan ei toimi, kokeillaan sokeasti vanhaa varmaa
        return genai.GenerativeModel("gemini-pro")
    
    return None

# --- 4. KÄYTTÖLIITTYMÄ JA LOGIIKKA ---
st.title("🕯️ Virtuaalinen Sukututkija")
st.markdown("Kysy minulta vanhoista termeistä, lähteistä tai tutkimusongelmista.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if api_key:
    genai.configure(api_key=api_key)
    
    if prompt := st.chat_input("Kirjoita kysymyksesi tähän..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Tutkitaan arkistoja..."):
                try:
                    # Kutsutaan älykästä valintafunktiota
                    model = hae_toimiva_malli()
                    
                    if model:
                        full_prompt = f"{SYSTEM_PROMPT}\n\nKäyttäjän kysymys: {prompt}"
                        response = model.generate_content(full_prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    else:
                        st.error("Yhtään tekoälymallia ei löytynyt. Tarkista API-avain.")
                        
                except Exception as e:
                    st.error(f"Tapahtui virhe: {e}")
                    st.info("Kokeile päivittää sivu.")
else:
    if not api_key:
        st.warning("Syötä API-avain sivupalkkiin aloittaaksesi.")

with st.sidebar:
    if st.button("Aloita uusi keskustelu"):
        st.session_state.messages = []
        st.rerun()
