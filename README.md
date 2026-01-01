# Sukututkimus-Kuraattori & Käsialatulkki 📜

**Sukututkimus-Kuraattori** on tekoälyavusteinen (AI) työkalu, joka on suunniteltu auttamaan sukututkijoita pääsemään yli tutkimuksen karikoista ("tiiliseinistä") ja tulkitsemaan vanhoja asiakirjoja.

Sovellus toimii virtuaalisena opettajana: se ei vain anna vastauksia, vaan ohjaa käyttäjää oikeiden suomalaisten lähdeaineistojen äärelle (mm. HisKi, SSHY, Kansallisarkisto).

## ✨ Ominaisuudet

* **🔍 Tutkimusongelmien analyysi:** Syötä sanallinen kuvaus ongelmasta (esim. kadonnut henkilö), ja tekoäly ehdottaa uusia hakustrategioita ja lähteitä.
* **🖋️ Vanhan käsialan tulkinta (Paleografia):** Lataa kuva (JPG/PNG) vanhasta kirkonkirjasta tai tuomiokirjasta. Tekoäly (GPT-4o) yrittää puhtaaksikirjoittaa tekstin rivi riviltä.
* **🎨 Visuaalinen käyttöliittymä:** Tunnelmallinen "vanha paperi" -teema ja helppokäyttöinen selainpohjainen käyttöliittymä.

## 🛠️ Tekninen toteutus

Sovellus on rakennettu Pythonilla hyödyntäen seuraavia kirjastoja:
* **Streamlit:** Käyttöliittymän luomiseen.
* **OpenAI API:** Tekoälyälyyn (käyttää `gpt-4o` -mallia, joka on välttämätön kuvien tulkinnassa).

## 🚀 Asennus ja käyttö

### 1. Esivaatimukset
* Asennettu [Python](https://www.python.org/) (versio 3.8 tai uudempi).
* Toimiva [OpenAI API-avain](https://platform.openai.com/). **Huom:** Avaimella pitää olla käyttöoikeus GPT-4o -malliin (vaatii yleensä pienen määrän saldoa tilillä).

### 2. Asenna riippuvuudet
Lataa projektin tiedostot ja aja seuraava komento terminaalissa projektikansiossa:

```bash
pip install -r requirements.txt
