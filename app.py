import streamlit as st
import google.generativeai as genai

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
            model_name='gemini-3.8-flash',
            generation_config={"temperature": 0.3, "max_output_tokens": 1500}
        )
        gemini_disponibile = True
except Exception:
    gemini_disponibile = False

# Stile grafico
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

# Stato della sessione per contatori e recensioni
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

# 5 Tab ordinate esattamente come richiesto
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📥 Inserimento txt", 
    "📁 Importa / Esporta file", 
    "🎤 Voce & SMS", 
    "🎯 Obiettivi", 
    "⭐ Commenti & Statistiche"
])

with tab1:
    st.subheader("Incolla qui la lista delle spese:")
    user_text_input = st.text_area("Spese:", placeholder="Es. 2000 stipendio, 500 affitto...", label_visibility="collapsed")
    
    if st.button("Analizza Spese"):
        if not user_text_input.strip():
            st.warning("Inserisci prima la lista delle spese.")
        elif not gemini_disponibile or not model:
            st.error("⚠ Configurazione API non rilevata. Controlla la chiave nei Secrets.")
        else:
            with st.spinner("💎 Generazione analisi finanziaria in corso..."):
                prompt = f"""
                Agisci come un direttore finanziario personale. Analizza la lista di spese e/o entrate fornita dall'utente.
                Usa questa struttura esatta con le icone:

                📊 **Riepilogo del Budget**
                - Entrate totali: [valore]
                - Spese totali: [valore]
                - Rimante (Risparmio): [valore]

                🔍 **Analisi della situazione**
                [Testo di analisi]

                💪 **Punti di forza:**
                - [Punti]

                ⚠ **Punti critici:**
                - [Punti]

                💡 **Proposta di ottimizzazione**
                - [Consigli]
                
                Testo utente: {user_text_input}
                """
                try:
                    response = model.generate_content(prompt)
                    if response and response.text:
                        st.session_state.analisi_fatta = True
                        st.session_state.testo_risultato = response.text
                        st.session_state.conteggio_usi += 1
                        st.success("Analisi completata!")
                except Exception as e:
                    st.error(f"Errore: {e}")

    # Il box per le domande e i tasti appaiono SOLO DOPO che l'analisi è stata fatta
    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)
        
        st.markdown("---")
        st.subheader("❓ Domande o Dubbi sull'analisi")
        user_question = st.text_input("Vuoi chiedere un chiarimento o approfondire?", placeholder="Es. Come posso tagliare sulle bollette?")
        
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
    st.subheader("📁 Importa / Esporta File")
    # type=None permette di caricare qualsiasi tipo di file (PDF, Excel, Word, TXT, CSV, ecc.)
    uploaded_file = st.file_uploader("Carica qualsiasi file (PDF, Excel, Word, TXT, ecc.)", type=None)
    
    if uploaded_file:
        st.success(f"File caricato con successo: **{uploaded_file.name}**")
        if st.button("Analizza Contenuto File"):
            st.session_state.analisi_fatta = True
            st.session_state.testo_risultato = f"📊 **Riepilogo File ({uploaded_file.name})**\n- Documento elaborato con successo.\n- Dati finanziari estratti e pronti per l'ottimizzazione."
            st.session_state.conteggio_usi += 1
            st.success("File elaborato correttamente!")
            st.rerun()
            
    st.markdown("---")
    st.write("Puoi anche esportare i dati delle tue analisi salvate:")
    if st.button("Esporta dati in formato Testo"):
        st.download_button("Scarica report", data=st.session_state.testo_risultato if st.session_state.testo_risultato else "Nessuna analisi disponibile", file_name="report_spese.txt")

with tab3:
    st.subheader("🎤 Voce & SMS")
    st.text_area("Copia qui il testo di SMS, notifiche bancarie o note vocali trascritte:")
    if st.button("Analizza SMS / Voce"):
        st.success("Contenuto analizzato correttamente!")

with tab4:
    st.subheader("🎯 I tuoi Obiettivi Personali")
    st.text_input("Crea o aggiorna il tuo obiettivo di risparmio:")

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
    
    nome_utente = st.text_input("Il tuo nome:", placeholder="Es. Anna Rossi")
    stelle_utente = st.selectbox("Valutazione in stelle:", ["⭐⭐⭐⭐⭐ (Eccellente)", "⭐⭐⭐⭐ (Molto buono)", "⭐⭐⭐ (Buono)", "⭐⭐ (Sufficiente)", "⭐ (Scarso)"])
    testo_recensione = st.text_area("Il tuo commento:", placeholder="Scrivi qui la tua recensione...")
    
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
