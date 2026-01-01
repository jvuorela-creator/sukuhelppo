import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Sukututkijan Tekstintunnistus", page_icon="📜")
st.title("📜 Vanhan käsialan tulkitsija")

# --- 1. API-avain ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.sidebar.warning("API-avain puuttuu asetuksista.")
    api_key = st.sidebar.text_input("Syötä Google API-avain:", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # --- 2. Etsitään toimivat mallit automaattisesti ---
        # Tämä estää "Model not found" -virheet, koska haemme vain ne, jotka ovat olemassa.
        available_models = []
        try:
            for m in genai.list_models():
                # Valitaan mallit, jotka tukevat sisällöntuotantoa
                if 'generateContent' in m.supported_generation_methods:
                    # Suositaan malleja, jotka ovat "latest" tai "flash"
                    available_models.append(m.name)
        except Exception as e:
            st.error(f"Virhe mallien haussa: {e}")

        # Jos lista on tyhjä, kirjasto on luultavasti liian vanha -> vaatii requirements.txt päivityksen
        if not available_models:
            st.error("Ei malleja saatavilla. Varmista, että requirements.txt sisältää: google-generativeai>=0.7.2")
        else:
            # Annetaan käyttäjän valita malli listasta
            # Yritetään valita oletuksena 'gemini-1.5-flash', jos se löytyy
            default_index = 0
            for i, name in enumerate(available_models):
                if "flash" in name:
                    default_index = i
                    break
            
            selected_model_name = st.selectbox("Valitse tekoälymalli:", available_models, index=default_index)
            model = genai.GenerativeModel(selected_model_name)

            # --- 3. Kuvan lataus ja käsittely ---
            uploaded_file = st.file_uploader("Valitse kuva", type=["jpg", "jpeg", "png"])

            if uploaded_file and st.button("🔍 Lue teksti"):
                image = Image.open(uploaded_file)
                st.image(image, caption='Tutkittava asiakirja', use_column_width=True)
                
                with st.spinner('Tekoäly tutkii käsialaa...'):
                    try:
                        prompt = "Litteroi (kirjoita puhtaaksi) kuvassa oleva teksti sana sanalta. Säilytä vanha kieliasu."
                        response = model.generate_content([prompt, image])
                        st.markdown("### Tulos:")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Virhe lukemisessa: {e}")
                        if "404" in str(e) or "not found" in str(e):
                             st.warning("Tämä malli ei ehkä tue kuvia. Kokeile valita listasta toinen malli (esim. joku, jossa lukee 'flash' tai 'vision').")

    except Exception as e:
        st.error(f"Yhteysvirhe: {e}")
else:
    st.info("Syötä API-avain aloittaaksesi.")
