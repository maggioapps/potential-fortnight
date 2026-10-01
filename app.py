import streamlit as st
import google.generativeai as genai
import io
import pypdf
from PIL import Image

# Configurazione della pagina
st.set_page_config(
    page_title="Split & Save AI",
    page_icon="💡",
    layout="centered"
)

# Configurazione Gemini con un limite di token bilanciato per evitare tagli
gemini_disponibile = False
model = None

try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name='gemini-3.8-flash',
            generation_config={"temperature": 0.4, "max_output_tokens": 2048}
        )
        gemini_disponibile = True
except Exception:
    gemini_disponibile = False

# Stile grafico avanzato
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 50%, #eff6ff 100%);
    }
    div.stMarkdown, .stTabs, .stFileUploader, .stTextArea, .stTextInput {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.2);
        margin-bottom: 12px;
    }
    h1, h2, h3 {
        color: #065f46 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Split & Save AI 💡")
st.write("Il tuo direttore finanziario personale e gratuito.")

# --- SIDEBAR: LINGUE, INSTALLAZIONE E INFO ---
st.sidebar.markdown("### 🌍 Selezione Lingua")
lista_lingue = [
    "Rilevamento Automatico (Auto)",
    "Italiano", "English", "Español", "Français", "Deutsch", 
    "Português", "Română", "العربية", "中文", "हिन्दी", 
    "日本語", "Русский", "Polski", "Nederlands", "Ελληνικά", 
    "Türkçe", "Українська", "Magyar", "Čeština", "Svenska", "한국어"
]
lingua_selezionata = st.sidebar.selectbox("Scegli la lingua:", lista_lingue)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⭐ Recensioni degli utenti")
st.sidebar.markdown("⭐⭐⭐⭐⭐ **4.9 / 5.0**")
st.sidebar.info("✨ *'Questa app mi ha svoltato la gestione del budget!'* — Marco R.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📱 Installa sul Telefono")
st.sidebar.info("Tocca i **tre puntini ⠇** in alto a destra e seleziona **'Aggiungi a schermata Home'**.")

# Stato della sessione
if "visite" not in st.session_state:
    st.session_state.visite = 1
if "conteggio_usi" not in st.session_state:
    st.session_state.conteggio_usi = 0
if "analisi_fatta" not in st.session_state:
    st.session_state.analisi_fatta = False
if "testo_risultato" not in st.session_state:
    st.session_state.testo_risultato = ""
if "recensioni" not in st.session_state:
    st.session_state.recensioni = [
        ("Marco R.", "⭐⭐⭐⭐⭐", "App fantastica!"),
        ("Giulia V.", "⭐⭐⭐⭐⭐", "Molto utile per risparmiare.")
    ]

# 5 Tab ordinate e complete
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📥 Inserimento txt", 
    "📁 Importa File & Foto", 
    "🎤 Voce & SMS", 
    "🎯 Obiettivi", 
    "⭐ Commenti & Statistiche"
])

# Funzione centrale con lunghezza bilanciata e ricca di dettagli specifici
def esegui_analisi_ia_profonda(contenuto_input, titolo_sorgente="Dati utente", is_image=False, image_obj=None, is_obiettivo=False):
    if not gemini_disponibile or not model:
        st.error("⚠ Configurazione API non rilevata. Controlla la chiave nei Secrets.")
        return
    
    with st.spinner("💎 Analisi finanziaria in corso..."):
        
        istruzione_lingua = ""
        if lingua_selezionata == "Rilevamento Automatico (Auto)":
            istruzione_lingua = "Rileva automaticamente la lingua e rispondi nella stessa."
        else:
            istruzione_lingua = f"Rispondi rigorosamente in lingua: {lingua_selezionata}."

        if is_obiettivo:
            prompt = f"""
            {istruzione_lingua}
            Agisci come un consulente finanziario spietato e diretto. L'utente ha inserito questo obiettivo: '{contenuto_input}'.
            Fornisci un'analisi completa ma concisa, citando cifre e dettagli specifici inseriti dall'utente.
            
            Usa questa struttura:
            📢 **Giudizio del Direttore sull'Obiettivo**
            (Congratulazioni se l'obiettivo è eccellente; commento pungente se mediocre; giudizio offensivo e tagliente se l'obiettivo è assurdo o scriteriato).
            
            🎯 **Analisi e Fattibilità** [Dettagli precisi e tempistiche]
            ⚠ **Ostacoli e Rischi** [Criticità reali]
            💡 **Piano d'Azione** [Passi concreti immediati]
            """
        else:
            prompt = f"""
            {istruzione_lingua}
            Agisci come un direttore finanziario spietato e senza filtri. Analizza i dati della sorgente: {titolo_sorgente}.
            Fornisci un'analisi strutturata, dettagliata ma della lunghezza giusta (senza dilungarti troppo ma senza troncare nulla), citando obbligatoriamente nomi specifici, esercenti, importi esatti, bonifici o categorie presenti nei dati.
            
            Usa questa struttura:
            📢 **Giudizio del Direttore**
            - Regole obbligatorie per il giudizio:
              1) Se il bilancio è POSITIVO (avanzo reale), fai i complimenti con lode calorosa.
              2) Se è NÉ POSITIVO NÉ NEGATIVO (pareggio o mediocre), fai un commento tagliente e un po' spinto sulla mediocrità.
              3) Se è NEGATIVO (passivo o sprechi), scrivi un commento sprezzante, duro e offensivo citando specificamente dove si buttano i soldi.

            📊 **Riepilogo Numerico** [Entrate, Spese, Margine esatto]
            🔍 **Analisi Dettagliata** [Cita voci, scontrini o transazioni specifiche senza girarci intorno]
            💡 **Tagli Immediati** [Azioni chirurgiche precise]
            """
        
        try:
            if is_image and image_obj is not None:
                response = model.generate_content([prompt, image_obj])
            else:
                full_prompt = prompt + f"\n\nDati / Testo fornito:\n{contenuto_input}"
                response = model.generate_content(full_prompt)
                
            if response and response.text:
                st.session_state.analisi_fatta = True
                st.session_state.testo_risultato = response.text
                st.session_state.conteggio_usi += 1
                st.success("Analisi completata!")
        except Exception as e:
            st.error(f"Errore durante l'analisi IA: {e}")

with tab1:
    st.subheader("Incolla qui la lista delle spese:")
    user_text_input = st.text_area("Spese:", placeholder="Es. 2000 stipendio, 500 affitto, 300 ristoranti...", label_visibility="collapsed", key="txt_input")
    
    if st.button("Analizza Spese in Profondità"):
        if not user_text_input.strip():
            st.warning("Inserisci prima la lista delle spese o dei movimenti.")
        else:
            esegui_analisi_ia_profonda(user_text_input, "Lista testuale")

    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)
        
        st.markdown("---")
        st.subheader("❓ Domande o Dubbi sull'analisi")
        user_question = st.text_input("Vuoi chiedere un chiarimento o approfondire?", placeholder="Es. Come posso tagliare sulle bollette?", key="q_tab1")
        
        col_1, col_2 = st.columns(2)
        with col_1:
            if st.button("Fai una domanda al consulente"):
                if user_question.strip() and model:
                    with st.spinner("Elaborazione risposta..."):
                        f_resp = model.generate_content(f"Rispondi in lingua {lingua_selezionata}, sii sintetico ma dettagliato, tagliente e specifico basandoti sull'analisi precedente: {user_question}")
                        if f_resp and f_resp.text:
                            st.markdown("### 💬 Risposta del Consulente:")
                            st.markdown(f_resp.text)
                            
        with col_2:
            if st.button("🔄 Nuova analisi"):
                st.session_state.analisi_fatta = False
                st.session_state.testo_risultato = ""
                st.rerun()

with tab2:
    st.subheader("📁 Importa File & 📷 Foto (PDF, TXT, CSV, JPG, PNG)")
    st.info("💡 Carica un documento PDF/CSV o scatta/carica la **foto di uno scontrino o di un estratto conto**.")
    
    uploaded_file = st.file_uploader("Carica file o foto", type=["pdf", "txt", "csv", "jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        file_name_lower = uploaded_file.name.lower()
        is_img_file = file_name_lower.endswith(('.jpg', '.jpeg', '.png'))
        
        if is_img_file:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"Foto caricata: {uploaded_file.name}", use_container_width=True)
        else:
            st.success(f"File caricato: **{uploaded_file.name}**")
        
        if st.button("🚀 Avvia Analisi Avanzata File / Foto"):
            try:
                bytes_data = uploaded_file.getvalue()
                
                if is_img_file:
                    image_obj = Image.open(io.BytesIO(bytes_data))
                    esegui_analisi_ia_profonda("", f"Foto scontrino/documento: {uploaded_file.name}", is_image=True, image_obj=image_obj)
                    st.rerun()
                    
                elif file_name_lower.endswith('.pdf'):
                    pdf_file_obj = io.BytesIO(bytes_data)
                    reader = pypdf.PdfReader(pdf_file_obj)
                    extracted_pages = []
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            extracted_pages.append(text)
                    testo_estratto = "\n".join(extracted_pages)
                    if not testo_estratto.strip():
                        testo_estratto = "Il PDF sembra scansionato o privo di testo vettoriale."
                    esegui_analisi_ia_profonda(testo_estratto[:30000], f"Documento PDF: {uploaded_file.name}")
                    st.rerun()
                    
                else:
                    testo_estratto = bytes_data.decode("utf-8", errors="ignore")
                    esegui_analisi_ia_profonda(testo_estratto[:30000], f"Documento: {uploaded_file.name}")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Errore durante l'elaborazione del file/foto: {e}")

    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)

    st.markdown("---")
    st.write("Esporta i dati delle tue analisi:")
    st.download_button("📥 Scarica report in formato Testo", data=st.session_state.testo_risultato if st.session_state.testo_risultato else "Nessuna analisi disponibile", file_name="report_spese.txt")

with tab3:
    st.subheader("🎤 Voce & SMS / Notifiche Bancarie")
    st.info("Incolla trascrizioni di note vocali o il testo di SMS/notifiche di spesa della tua banca.")
    sms_voce_input = st.text_area("Testo SMS o trascrizione vocale:", placeholder="Es. 'Hai speso 45.50 EUR presso Supermercato con carta finita in 1234'...", key="sms_input")
    
    if st.button("Analizza SMS / Voce in Profondità"):
        if not sms_voce_input.strip():
            st.warning("Inserisci prima il testo da analizzare.")
        else:
            esegui_analisi_ia_profonda(sms_voce_input, "SMS / Nota Vocale")

    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)

with tab4:
    st.subheader("🎯 I tuoi Obiettivi Personali di Risparmio")
    st.info("Imposta un obiettivo e lascia che l'IA calcoli un piano strategico avanzato su misura.")
    
    obiettivo_input = st.text_input("Descrivi il tuo obiettivo:", placeholder="Es. Vorrei risparmiare 3000 euro per una vacanza in Giappone entro 10 mesi.")
    
    if st.button("Genera Piano Strategico Obiettivo"):
        if not obiettivo_input.strip():
            st.warning("Inserisci prima il tuo obiettivo.")
        else:
            esegui_analisi_ia_profonda(obiettivo_input, "Obiettivo di Risparmio", is_obiettivo=True)

    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)

with tab5:
    st.subheader("📊 Statistiche di Utilizzo dell'App")
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.metric(label="👥 Persone passate", value=st.session_state.visite)
    with col_stat2:
        st.metric(label="🚀 Analisi effettuate", value=st.session_state.conteggio_usi)

    st.markdown("---")
    st.subheader("⭐ Lascia un Commento e una Valutazione")
    st.write("Fai sapere agli altri cosa pensi dell'applicazione!")
    
    nome_utente = st.text_input("Il tuo nome:", placeholder="Es. Anna Rossi", key="nome_rec")
    stelle_utente = st.selectbox("Valutazione in stelle:", ["⭐⭐⭐⭐⭐ (Eccellente)", "⭐⭐⭐⭐ (Molto buono)", "⭐⭐⭐ (Buono)", "⭐⭐ (Sufficiente)", "⭐ (Scarso)"])
    testo_recensione = st.text_area("Il tuo commento:", placeholder="Scrivi qui la tua recensione...", key="testo_rec")
    
    if st.button("Invia Commento"):
        if nome_utente.strip() and testo_recensione.strip():
            st.session_state.recensioni.insert(0, (nome_utente, stelle_utente.split(" ")[0], testo_recensione))
            st.success("🎉 Grazie mille per il tuo commento!")
        else:
            st.warning("Inserisci il tuo nome e il commento prima di inviare.")
            
    st.markdown("---")
    st.subheader("📋 Commenti della Community")
    for utente, stelle, commento in st.session_state.recensioni:
        st.markdown(f"**{utente}** - {stelle}\n\n*{commento}*")
        st.markdown("---")
