import streamlit as st
import google.generativeai as genai
from PIL import Image # Tarvitaan kuvan avaamiseen

# --- SIVUN ASETUKSET ---
st.set_page_config(
    page_title="Sukututkimus-Kuraattori (Gemini)",
    page_icon="📜",
    layout="centered"
)

# --- CSS-TYYLITTELY (SAMA KUIN ENNEN) ---
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
[data-testid="stHeader"] { background: transparent; }
.main-container {
    background-color: rgba(255, 252, 240, 0.95);
    padding: 30px;
    border-radius: 10px;
    border: 1px solid #d4c5a9;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
h1, h2, h3 { color: #4a3b2a !important; font-family: 'Georgia', serif; }
.stTextArea textarea, .stTextInput input { background-color: #fffefb !important; border: 1px solid #bda886 !important; }
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# --- SIVUPALKKI ---
with st.sidebar:
    st.header("⚙️ Asetukset")
    st.write("Moottorina toimii Google Gemini 1.5 Flash.")
    
    # API-avaimen syöttö
    api_key = st.text_input("Syötä Google Gemini API-avain:", type="password")
    st.info("Hanki ilmainen avain: aistudio.google.com")
    
    st.markdown("---")
    st.write("**Vinkki:** Gemini osaa lukea vanhaa käsialaa erittäin nopeasti.")

# --- PÄÄOHJELMA ---
def main():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.title("📜 Sukututkimus-Kuraattori")
    st.caption("Powered by Google Gemini")
    
    st.write("""
    **Tervetuloa.** Voit käyttää tätä työkalua kahdella tavalla:
    1. **Analyysi:** Kuvaile tutkimusongelma sanallisesti.
    2. **Käsiala:** Lataa kuva vanhasta tekstistä tulkattavaksi.
    """)
    
    st.markdown("---")

    # 1. TEKSTIKENTTÄ
    st.subheader("1. Ongelman kuvaus tai lisätiedot")
    user_problem_text = st.text_area(
        "Kirjoita tähän:", 
        height=100, 
        placeholder="Esim. Mitä tässä kuvassa lukee? TAI: Matti Meikäläinen katoaa vuonna 1875..."
    )

    # 2. KUVAN LATAUS
    st.subheader("2. Lataa kuva (valinnainen)")
    uploaded_image = st.file_uploader("Valitse kuva (JPG, PNG):", type=["jpg", "jpeg", "png"])
    
    img = None
    if uploaded_image is not None:
        # Avataan kuva PIL-kirjastolla, jotta Gemini ymmärtää sen
        img = Image.open(uploaded_image)
        st.image(img, caption="Ladattu kuva", use_column_width=True)

    st.markdown("---")

    # TOIMINTOLOKIIKKA
    if st.button("🔍 Analysoi / Tulkitse"):
        if not api_key:
            st.error("⚠️ Syötä ensin API-avain sivupalkkiin.")
            return

        try:
            # Konfiguroidaan Gemini
            genai.configure(api_key=api_key)
            
            # Valitaan malli. 'gemini-1.5-flash' on nopea ja hyvä kuvissa.
            # Voit käyttää myös 'gemini-1.5-pro', jos haluat syvempää päättelykykyä.
            
            with st.spinner('Tekoäly tutkii aineistoa...'):
                
                # --- TILANNE A: KUVA MUKANA (Käsialan tulkinta) ---
                if img:
                    # Määritellään rooli mallille
                    model = genai.GenerativeModel('gemini-pro'),
                        system_instruction="""Olet kokenut paleografi ja vanhojen suomalaisten/ruotsalaisten asiakirjojen asiantuntija. 
                        Tehtäväsi on puhtaaksikirjoittaa kuvassa näkyvä teksti.
                        1. Kirjoita teksti rivi riviltä.
                        2. Merkitse epäselvät kohdat [?].
                        3. Kerro lopuksi lyhyesti, mikä asiakirja on kyseessä (esim. rippikirja)."""
                    )
                    
                    # Lähetetään teksti JA kuva listana
                    prompt_content = ["Tulkitse tämä vanha asiakirja.", img]
                    if user_problem_text:
                        prompt_content.append(f"Käyttäjän lisätiedot: {user_problem_text}")

                    response = model.generate_content(prompt_content)
                    
                    st.markdown("### 🖋️ Tulkinta käsialasta:")
                    st.write(response.text)

                # --- TILANNE B: VAIN TEKSTI (Tutkimusongelma) ---
                else:
                    if len(user_problem_text) < 5:
                        st.warning("Kirjoita tarkempi kuvaus ongelmasta.")
                        return

                    model = genai.GenerativeModel(
                        model_name="gemini-1.5-flash",
                        system_instruction="""Olet kokenut suomalainen sukututkimuksen opettaja.
                        Tehtäväsi on auttaa käyttäjää löytämään uusia lähteitä.
                        Älä keksi faktoja. Ehdota lähteitä kuten HisKi, SSHY, Kansallisarkisto, Henkikirjat.
                        Ole kannustava."""
                    )
                    
                    response = model.generate_content(user_problem_text)
                    
                    st.markdown("### 💡 Ehdotetut tutkimussuunnat:")
                    st.write(response.text)

        except Exception as e:
            st.error(f"Tapahtui virhe: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

