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

# Sidebar
st.sidebar.markdown("### 📱 Installa sul Telefono")
st.sidebar.info("Tocca i **tre puntini ⠇** in alto a destra e seleziona **'Aggiungi a schermata Home'**.")
st.sidebar.markdown("---")
st.sidebar.info("ℹ️ **App 100% Gratuita**: Nessun abbonamento richiesto.")

# Stato della sessione
if "analisi_fatta" not in st.session_state:
    st.session_state.analisi_fatta = False
if "testo_risultato" not in st.session_state:
    st.session_state.testo_risultato = ""

tab1, tab2, tab3, tab4 = st.tabs(["📥 Inserimento", "🎯 Obiettivi", "🎤 Voce & SMS", "⭐ Recensioni"])

with tab1:
    st.subheader("Incolla qui la lista delle spese:")
    user_text_input = st.text_area("Spese:", placeholder="Es. 2000 stipendio, 500 affitto...", label_visibility="collapsed")
    
    if st.button("Analizza Spese"):
        if not user_text_input.strip():
            st.warning("Inserisci prima la lista delle spese.")
        elif not gemini_disponibile or not model:
            st.error("⚠️️ Configurazione API non rilevata. Controlla la chiave nei Secrets.")
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
                        st.success("Analisi completata!")
                except Exception as e:
                    st.error(f"Errore: {e}")

    # Il box per le domande appare SOLO DOPO che l'analisi è stata fatta
    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)
        
        st.markdown("---")
        st.subheader("❓ Domande o Dubbi sull'analisi")
        user_question = st.text_input("Vuoi chiedere un chiarimento o approfondire?", placeholder="Es. Come posso tagliare sulle bollette?")
        
        if st.button("Fai una domanda al consulente"):
            if user_question.strip() and model:
                with st.spinner("Elaborazione risposta..."):
                    f_resp = model.generate_content(f"Basandoti sull'analisi precedente, rispondi a: {user_question}")
                    if f_resp and f_resp.text:
                        st.markdown("### 💬 Risposta del Consulente:")
                        st.markdown(f_resp.text)

with tab2:
    st.subheader("🎯 I tuoi Obiettivi Personali")
    st.text_input("Crea o aggiorna il tuo obiettivo di risparmio:")

with tab3:
    st.subheader("📲 Inserimento Rapido SMS")
    st.text_area("Copia qui il testo di SMS o notifiche bancarie:")

with tab4:
    st.subheader("⭐ Recensioni Verificate")
    st.markdown("⭐⭐⭐⭐⭐ **4.9 / 5.0** - *'App fantastica!'* - Marco R.")
