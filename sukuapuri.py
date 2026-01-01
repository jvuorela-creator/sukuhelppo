import streamlit as st
import google.generativeai as genai
import os
import random

# --- SIVUN ASETUKSET ---
st.set_page_config(
    page_title="Virtuaalinen Sukututkija",
    page_icon="🕯️",
    layout="wide" # Vaihdetaan 'wide'-tilaan, jotta kuville on enemmän tilaa
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

# --- CSS-TYYLITTELY (VANHA PAPERI & FONTIT) ---
page_bg_img = """
<style>
/* Taustakuva (kartta) */
.stApp {
    background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Karta_öfver_Helsingfors_med_dess_invid_liggande_trakter_1776_-_Kansallisarkisto.jpg/1280px-Karta_öfver_Helsingfors_med_dess_invid_liggande_trakter_1776_-_Kansallisarkisto.jpg");
    background-size: cover;
    background-attachment: fixed;
    background-blend-mode: overlay;
}
/* Himmennyskalvo tekstin alle */
.stApp::before {
    content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(250, 245, 235, 0.92); z-index: -1;
}
h1, h2, h3 { font-family: 'Georgia', serif; color: #4a3b2a; text-shadow: 1px 1px 0px #fff; }
.stChatMessage { background-color: #fffaf0; border-radius: 10px; border: 1px solid #dcd0c0; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
/* Sivupalkin tyyli */
section[data-testid="stSidebar"] {
    background-color: rgba(245, 240, 230, 0.95);
    border-right: 1px solid #d4c4b0;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# --- KUVA-AARTEET (Lista julkisista historiallisista kuvista) ---
kuva_arkisto = [
    {"url": "https
