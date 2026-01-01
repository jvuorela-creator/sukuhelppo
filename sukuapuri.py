import streamlit as st
import google.generativeai as genai
from PIL import Image

# Sivun asetukset
st.set_page_config(page_title="Sukututkijan Tekstintunnistus", page_icon="📜")

st.title("📜 Vanhan käsialan tulkitsija")
st.write("Lataa kuva kirkonkirjasta tai vanhasta kirjeestä, niin tekoäly yrittää lukea sen.")

# --- 1. API-avaimen hallinta ---
# Yritetään hakea avain Streamlitin "Secrets"-piilopaikasta.
# Jos sitä ei ole siellä, kysytään sitä käyttäjältä sivupalkissa.
api_key = None

if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.sidebar.warning("API-avainta ei löytynyt asetuksista.")
    api_key = st.sidebar.text_input("Syötä Google API-avain tähän:", type="password")

# --- 2. Sovelluksen päälogiikka ---
if api_key:
    try:
        # Konfiguroidaan tekoäly avaimella
        genai.configure(api_key=api_key)
        
        # KORJAUS: Käytetään "gemini-pro" mallia, joka on yhteensopivin
        # vanhempien kirjastoversioiden kanssa Streamlit Cloudissa.
        model = genai.GenerativeModel('gemini-pro')

        # Kuvan lataus
        uploaded_file = st.file_uploader("Valitse kuva (JPG, PNG)", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            # Näytetään ladattu kuva
            image = Image.open(uploaded_file)
            st.image(image, caption='Ladattu asiakirja', use_column_width=True)

            # Analyysi-nappi
            if st.button("🔍 Lue teksti"):
                with st.spinner('Tutkitaan vanhaa käsialaa...'):
                    try:
                        # Erityinen ohjeistus sukututkimusaineistolle
                        prompt = """
                        Toimi asiantuntevana sukututkijana. 
                        Litteroi (kirjoita puhtaaksi) tässä kuvassa oleva teksti mahdollisimman tarkasti.
                        Jos kuvassa on vanhaa käsialaa (esim. kirkonkirja), säilytä alkuperäinen kirjoitusasu.
                        Jos jokin sana on epäselvä, merkitse se [?].
                        """
                        
                        # Lähetetään pyyntö (huom: gemini-pro ottaa kuvan ja tekstin listana)
                        response = model.generate_content([prompt, image])
                        
                        st.success("Valmis!")
                        st.markdown("### Tulkittu teksti:")
                        st.write(response.text)
                        
                    except Exception as e:
                        st.error(f"Virhe analyysissa: {e}")
                        st.info("Vinkki: Jos virhe liittyy 'block reason' -viestiin, tekoäly on saattanut tulkita kuvan turvallisuussääntöjen vastaiseksi.")

    except Exception as e:
        st.error(f"Virhe API-yhteydessä: {e}")
        st.write("Tarkista, että API-avain on varmasti oikein.")

else:
    st.info("👈 Syötä ensin API-avain vasempaan palkkiin jatkaaksesi.")
