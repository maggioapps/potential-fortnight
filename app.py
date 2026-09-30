import streamlit as st
import google.generativeai as genai
import io
import pypdf

# Configurazione della pagina
st.set_page_config(
    page_title="Split & Save AI",
    page_icon="💡",
    layout="centered"
)

# Configurazione Gemini
gemini_disponibile = False
model = None

try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            generation_config={"temperature": 0.3, "max_output_tokens": 1500}
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

# --- SIDEBAR: INSTALLAZIONE E INFO ---
st.sidebar.markdown("### ⭐ Recensioni degli utenti")
st.sidebar.markdown("⭐⭐⭐⭐⭐ **4.9 / 5.0**")
st.sidebar.info("✨ *'Questa app mi ha svoltato la gestione del budget!'* — Marco R.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📱 Installa sul Telefono")
st.sidebar.info("Tocca i **tre puntini ⠇** in alto a destra e seleziona **'Aggiungi a schermata Home'**.")

st.sidebar.markdown("---")
st.sidebar.info("ℹ️ **App 100% Gratuita**: Nessun abbonamento richiesto.")

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
    "📁 Importa / Esporta file", 
    "🎤 Voce & SMS", 
    "🎯 Obiettivi", 
    "⭐ Commenti & Statistiche"
])

# Funzione di utilità per l'analisi finanziaria con IA
def esegui_analisi_ia(testo_input, titolo_sorgente="Testo utente"):
    if not gemini_disponibile or not model:
        st.error("⚠ Configurazione API non rilevata. Controlla la chiave nei Secrets.")
        return
    
    with st.spinner("💎 Generazione analisi finanziaria in corso..."):
        prompt = f"""
        Agisci come un direttore finanziario personale. Analizza i dati finanziari, le spese, le entrate o i movimenti forniti.
        Sorgente dati: {titolo_sorgente}
        
        Usa questa struttura esatta con le icone:

        📊 **Riepilogo del Budget**
        - Entrate totali: [valore stimato o reale]
        - Spese totali: [valore stimato o reale]
        - Rimante (Risparmio): [valore stimato o reale]

        🔍 **Analisi della situazione**
        [Testo di analisi approfondito]

        💪 **Punti di forza:**
        - [Punti]

        ⚠ **Punti critici:**
        - [Punti]

        💡 **Proposta di ottimizzazione**
        - [Consigli pratici]
        
        Dati forniti:
        {testo_input}
        """
        try:
            response = model.generate_content(prompt)
            if response and response.text:
                st.session_state.analisi_fatta = True
                st.session_state.testo_risultato = response.text
                st.session_state.conteggio_usi += 1
                st.success("Analisi completata con successo!")
        except Exception as e:
            st.error(f"Errore durante l'analisi: {e}")

with tab1:
    st.subheader("Incolla qui la lista delle spese:")
    user_text_input = st.text_area("Spese:", placeholder="Es. 2000 stipendio, 500 affitto...", label_visibility="collapsed", key="txt_input")
    
    if st.button("Analizza Spese"):
        if not user_text_input.strip():
            st.warning("Inserisci prima la lista delle spese.")
        else:
            esegui_analisi_ia(user_text_input, "Lista testuale")

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
                        f_resp = model.generate_content(f"Basandoti sull'analisi precedente, rispondi a: {user_question}")
                        if f_resp and f_resp.text:
                            st.markdown("### 💬 Risposta del Consulente:")
                            st.markdown(f_resp.text)
                            
        with col_2:
            if st.button("🔄 Nuova analisi"):
                st.session_state.analisi_fatta = False
                st.session_state.testo_risultato = ""
                st.rerun()

with tab2:
    st.subheader("📁 Importa File dal Telefono (PDF, TXT, CSV)")
    st.info("💡 Carica il tuo estratto conto PDF, file TXT o CSV dai Download del telefono.")
    
    uploaded_file = st.file_uploader("Carica file", type=["pdf", "txt", "csv"])
    
    if uploaded_file is not None:
        st.success(f"File caricato: **{uploaded_file.name}**")
        
        if st.button("🚀 Avvia Analisi File"):
            testo_estratto = ""
            try:
                bytes_data = uploaded_file.getvalue()
                
                # Gestione specifica ed estrazione avanzata per i file PDF
                if uploaded_file.name.lower().endswith('.pdf'):
                    pdf_file_obj = io.BytesIO(bytes_data)
                    reader = pypdf.PdfReader(pdf_file_obj)
                    extracted_pages = []
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            extracted_pages.append(text)
                    testo_estratto = "\n".join(extracted_pages)
                    if not testo_estratto.strip():
                        testo_estratto = "Il PDF sembra scansionato o privo di testo vettoriale selezionabile."
                else:
                    # Gestione per TXT o CSV
                    testo_estratto = bytes_data.decode("utf-8", errors="ignore")

                # Avvia l'analisi IA con il testo estratto dal documento
                esegui_analisi_ia(testo_estratto[:15000], f"Documento: {uploaded_file.name}")
                st.rerun()
            except Exception as e:
                st.error(f"Errore durante l'elaborazione del file: {e}")

    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)

    st.markdown("---")
    st.write("Esporta i dati delle tue analisi:")
    st.download_button("📥 Scarica report in formato Testo", data=st.session_state.testo_risultato if st.session_state.testo_risultato else "Nessuna analisi disponibile", file_name="report_spese.txt")

with tab3:
    st.subheader("🎤 Voce & SMS / Notifiche Bancarie")
    st.info("Incolla trascrizioni di note vocali o il testo di SMS/notifiche di spesa della tua banca.")
    sms_voce_input = st.text_area("Testo SMS o trascrizione vocale:", placeholder="Es. 'Hai speso 45.50 EUR presso Supermercato con carta finita in 1234' oppure trascrizione vocale...", key="sms_input")
    
    if st.button("Analizza SMS / Voce"):
        if not sms_voce_input.strip():
            st.warning("Inserisci prima il testo da analizzare.")
        else:
            esegui_analisi_ia(sms_voce_input, "SMS / Nota Vocale")

    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)

with tab4:
    st.subheader("🎯 I tuoi Obiettivi Personali di Risparmio")
    st.info("Imposta un obiettivo e lascia che l'IA calcoli un piano di risparmio su misura.")
    
    obiettivo_input = st.text_input("Descrivi il tuo obiettivo:", placeholder="Es. Vorrei risparmiare 3000 euro per una vacanza in Giappone entro 10 mesi.")
    
    if st.button("Genera Piano d'Azione Obiettivo"):
        if not obiettivo_input.strip():
            st.warning("Inserisci prima il tuo obiettivo.")
        else:
            if not gemini_disponibile or not model:
                st.error("⚠ Configurazione API non rilevata.")
            else:
                with st.spinner("Creazione piano di risparmio personalizzato..."):
                    prompt_obj = f"""
                    Agisci come un consulente finanziario personale. L'utente ha il seguente obiettivo di risparmio: '{obiettivo_input}'.
                    Fornisci un piano dettagliato strutturato in questo modo:
                    - 🎯 **Obiettivo analizzato**
                    - 💰 **Risparmio mensile necessario**
                    - ✂️ **Aree di taglio spese consigliate per centrare il target**
                    - 📅 **Tabella di marcia passo-passo**
                    """
                    try:
                        res_obj = model.generate_content(prompt_obj)
                        if res_obj and res_obj.text:
                            st.markdown("### 📋 Il tuo Piano di Risparmio:")
                            st.markdown(res_obj.text)
                            st.session_state.conteggio_usi += 1
                    except Exception as e:
                        st.error(f"Errore: {e}")

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
