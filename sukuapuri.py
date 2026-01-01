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
# Taustakuva
bg_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Karta_öfver_Helsingfors_med_dess_invid_liggande_trakter_1776_-_Kansallisarkisto.jpg/1280px-Karta_öfver_Helsingfors_med_dess_invid_liggande_trakter_1776_-_Kansallisarkisto.jpg"

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

# --- 1. API-AVAIMEN HAKU ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.sidebar.error("API-avain puuttuu secrets-tiedostosta.")

# --- 2. SIVUPALKKI (HTML-kuvat) ---
with st.sidebar:
    st.title("📜 Arkiston kätköistä")
    st.markdown("---")
    
    # Määritellään kuvat suoraan HTML-muotoon sopiviksi
    # Tämä kiertää Streamlitin latausongelmat
    kuvat = [
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Lastukoski_crop.jpg/640px-Lastukoski_crop.jpg", "Tukkilaisten elämää"),
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Pudasjarvi_church_book.jpg/640px-Pudasjarvi_church_book.jpg", "Vanha kirkonkirja"),
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Savupirtti_Kortteeria.jpg/640px-Savupirtti_Kortteeria.jpg", "Savupirtti"),
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Albert_Edelfelt_-_Women_of_Ruokolahti_on_the_Church_Hill_-_Google_Art_Project.jpg/640px-Albert_Edelfelt_-_Women_of_Ruokolahti_on_the_Church_Hill_-_Google_Art_Project.jpg", "Ruokolahden eukkoja"),
        ("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Juho_Rissanen_-_By_the_Source.jpg/640px-Juho_Rissanen_-_By_the_Source.jpg", "Lähteellä")
    ]
    
    # Arvotaan ja näytetään HTML-koodilla
    valinnat = random.sample(kuvat, 2)
    
    for url, teksti in valinnat:
        html_code = f"""
        <div style="margin-bottom: 20px; text-align: center;">
            <img src="{url}" style="width: 100%; border-radius: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
            <p style="font-size: 0.9em; font-style: italic; color: #555; margin-top: 5px;">{teksti}</p>
        </div>
        """
        st.markdown(html_code, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 Tyhjennä keskustelu"):
        st.session_state.messages = []
        st.rerun()

# --- 3. PÄÄNÄKYMÄ ---
col1, col2 = st.columns([1, 4])
with col1:
    # Ikoni myös HTML:nä varmuuden vuoksi
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
