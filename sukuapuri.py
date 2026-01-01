import streamlit as st
from openai import OpenAI
import base64 # Tarvitaan kuvien käsittelyyn

# --- SIVUN ASETUKSET ---
st.set_page_config(
    page_title="Sukututkimus-Kuraattori",
    page_icon="📜",
    layout="centered"
)

# --- APUFUNKTIO KUVAN KOODAAMISEEN ---
# OpenAI:n API vaatii kuvan base64-koodattuna merkkijonona.
def encode_image_to_base64(uploaded_file):
    if uploaded_file is not None:
        # Palautetaan tiedoston sisältö base64-muodossa
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    return None

# --- CSS-TYYLITTELY (VISUAALINEN ILME) ---
# Pidetään sama vanha paperi -teema
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

.main-container {
    background-color: rgba(255, 252, 240, 0.95);
    padding: 30px;
    border-radius: 10px;
    border: 1px solid #d4c5a9;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

h1, h2, h3 {
    color: #4a3b2a !important;
    font-family: 'Georgia', serif;
}

.stTextArea textarea, .stTextInput input {
    background-color: #fffefb !important;
    border: 1px solid #bda886 !important;
}

/* Tyylitellään tiedoston lataaja sopimaan teemaan */
[data-testid="stFileUploader"] {
    border: 1px dashed #bda886;
    padding: 10px;
    border-radius: 5px;
    background-color: #fffefb;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# --- SIVUPALKKI (ASETUKSET) ---
with st.sidebar:
    st.header("⚙️ Asetukset")
    st.write("Tämä sovellus käyttää tekoälyä (GPT-4o) sukututkimusongelmien ja vanhojen käsialojen ratkaisuun.")
    
    # API-avaimen syöttö turvallisesti
    # HUOM: Käsialan tunnistus vaatii maksullisen GPT-4o mallin käyttöä.
    api_key = st.text_input("Syötä OpenAI API-avain:", type="password")
    st.info("Hanki avain: platform.openai.com. Varmista että tililläsi on saldoa.")
    
    st.markdown("---")
    st.write("**Vinkki:** Käsialan tunnistuksessa paras tulos tulee terävällä, hyvässä valossa otetulla kuvalla.")

# --- PÄÄOHJELMA ---
def main():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.title("📜 Sukututkimus-Kuraattori & Käsialatulkki")
    st.write("""
    **Tervetuloa.** Voit käyttää tätä työkalua kahdella tavalla:
    1. Kuvaile sanallisesti tutkimusongelma.
    2. Lataa kuva vanhasta tekstistä, ja tekoäly yrittää lukea sen.
    """)
    
    st.markdown("---")

    # 1. TEKSTIKENTTÄ ONGELMALLE
    st.subheader("1. Tutkimusongelman kuvaus")
    user_problem_text = st.text_area(
        "Kirjoita ongelma tai lisätietoja ladatusta kuvasta:", 
        height=100, 
        placeholder="Esim. Matti Meikäläinen katoaa vuonna 1875... TAI: Ohessa kuva Turun rippikirjasta, mitä rivillä 5 lukee?"
    )

    # 2. KUVAN LATAUS
    st.subheader("2. Lataa kuva käsialasta (valinnainen)")
    uploaded_image = st.file_uploader("Valitse kuva (JPG, PNG):", type=["jpg", "jpeg", "png"])
    
    if uploaded_image is not None:
        # Näytetään esikatselu ladatusta kuvasta
        st.image(uploaded_image, caption="Ladattu kuva", use_column_width=True)

    st.markdown("---")

    # ANALYSOINTIPAINIKE
    if st.button("🔍 Analysoi / Tulkitse"):
        if not api_key:
            st.error("⚠️ Syötä ensin API-avain sivupalkkiin.")
            return

        client = OpenAI(api_key=api_key)
        
        # --- HAARA 1: KUVAN TULKINTA (Jos kuva on ladattu) ---
        if uploaded_image is not None:
            with st.spinner('Tekoäly tutkii käsialaa (tämä voi kestää hetken)...'):
                try:
                    # 1. Koodataan kuva base64-muotoon lähetystä varten
                    base64_image = encode_image_to_base64(uploaded_image)

                    # 2. Määritellään paleografian asiantuntijan rooli
                    handwriting_system_prompt = """
                    Olet kokenut paleografi ja vanhojen suomalaisten/ruotsalaisten asiakirjojen asiantuntija (1700-1900 -luvut).
                    Tehtäväsi on puhtaaksikirjoittaa (transkriboida) kuvassa näkyvä teksti mahdollisimman tarkasti.
                    
                    Toimintaohjeet:
                    - Kirjoita teksti rivi riviltä, kuten se kuvassa on.
                    - Jos olet epävarma sanasta tai kirjaimesta, merkitse se hakasulkeisiin ja kysymysmerkillä, esim. [Sukunimi?].
                    - Jos kuvassa on selkeitä sarakkeita (kuten rippikirjassa), yritä säilyttää rakenne.
                    - Lopuksi anna lyhyt arvio siitä, mikä asiakirjatyyppi on kyseessä ja millä kielellä se todennäköisesti on.
                    """

                    # 3. Rakennetaan viesti tekoälylle (teksti + kuva)
                    messages = [
                        {"role": "system", "content": handwriting_system_prompt},
                        {"role": "user", "content": [
                            {"type": "text", "text": f"Ole hyvä ja tulkitse tämä kuva. Käyttäjän lisätiedot: {user_problem_text}"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]}
                    ]

                    # 4. Kutsutaan mallia (GPT-4o on välttämätön kuvien kanssa)
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        max_tokens=800 # Rajoitetaan vastauksen pituutta kustannusten hallitsemiseksi
                    )
                    
                    st.markdown("### 🖋️ Tulkinta käsialasta:")
                    st.write(response.choices[0].message.content)
                    st.success("Huom: Tekoäly voi tehdä virheitä vaikeissa käsialoissa. Tarkista aina tulos alkuperäisestä lähteestä.")

                except Exception as e:
                    st.error(f"Virhe kuvan käsittelyssä: {e}")

        # --- HAARA 2: PELKKÄ TEKSTIONGELMA (Jos kuvaa EI ole ladattu) ---
        elif user_problem_text and len(user_problem_text) > 10:
            with st.spinner('Tutkitaan virtuaalisia arkistoja ja mietitään ratkaisua...'):
                try:
                    # Perus sukututkimus-prompti (sama kuin aiemmin)
                    genealogy_system_prompt = """
                    Olet kokenut suomalainen sukututkija ja opettaja. Tehtäväsi on auttaa käyttäjää pääsemään eteenpäin tutkimuksessaan.
                    Älä keksi faktoja. Ehdota konkreettisia suomalaisia lähdeaineistoja (HisKi, SSHY, Kansallisarkisto, Henkikirjat, Tuomiokirjat) ja loogisia päättelyketjuja.
                    Vastaa suomeksi, kannustavalla ja asiantuntevalla sävyllä.
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": genealogy_system_prompt},
                            {"role": "user", "content": user_problem_text}
                        ]
                    )
                    
                    st.markdown("### 💡 Ehdotetut tutkimussuunnat:")
                    st.write(response.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"Tapahtui virhe: {e}")
        else:
            st.warning("Syötä joko kuvaus ongelmasta tai lataa kuva tulkittavaksi.")

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()