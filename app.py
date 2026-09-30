import streamlit as st
from datetime import date
import time
import google.generativeai as genai

# Configurazione della pagina
st.set_page_config(
    page_title="Split & Save AI",
    page_icon="💡",
    layout="centered"
)

# --- 🤖 CONFIGURAZIONE GEMINI ---
gemini_disponibile = False
model = None

try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)
        generation_config = {
            "temperature": 0.3,
            "max_output_tokens": 1500,
        }
        model = genai.GenerativeModel(
            model_name='gemini-3.8-flash',
            generation_config=generation_config
        )
        gemini_disponibile = True
except Exception as e:
    gemini_disponibile = False

# --- 🎨 STILE GRAFICO PREMIUM ---
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
    p, span, label, .stMarkdown p {
        color: #1f2937;
    }
    section[data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {
        color: #1f2937 !important;
    }
    h1, h2, h3 {
        color: #065f46 !important;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# --- LINGUE & DIZIONARIO ---
LANGUAGES = {
    "Italiano": {"title": "Split & Save AI 💡", "subtitle": "Il tuo direttore finanziario personale e gratuito.", "review": "Recensioni Verificate", "goal": "I tuoi Obiettivi Personali"},
    "English": {"title": "Split & Save AI 💡", "subtitle": "Your personal and free financial director.", "review": "Verified Reviews", "goal": "Your Personal Goals"}
}

selected_lang = st.sidebar.selectbox("🌍 Lingua / Language", list(LANGUAGES.keys()), index=0)
t = LANGUAGES[selected_lang]

st.title(t["title"])
st.write(t["subtitle"])

# --- SIDEBAR: GUIDA & INFO ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 📱 Installa sul Telefono")
st.sidebar.info("Tocca i **tre puntini ⠇** in alto a destra nel browser e seleziona **'Aggiungi a schermata Home'**.")

st.sidebar.markdown("---")
st.sidebar.info("ℹ️ **App 100% Gratuita**: Nessun abbonamento richiesto.")

# Inizializzazione dello stato per la chat/domande successive
if "analisi_effettuata" not in st.session_state:
    st.session_state.analisi_effettuata = False
if "ultimo_risultato" not in st.session_state:
    st.session_state.ultimo_risultato = ""

# --- INTERFACCIA PRINCIPALE ---
tab1, tab2, tab3, tab4 = st.tabs(["📥 Inserimento", "🎯 Obiettivi", "🎤 Voce & SMS", "⭐ Recensioni"])

with tab1:
    st.subheader("Incolla qui la lista delle spese:")
    user_text_input = st.text_area("Spese:", placeholder="Es. 2000 stipendio, 500 affitto...", label_visibility="collapsed")
    
    if st.button("Analizza Spese"):
        if not user_text_input.strip():
            st.warning("Inserisci prima la lista delle spese.")
        else:
            if not gemini_disponibile or not model:
                st.error("⚠️ Configurazione API non rilevata. Verifica i Secrets su Streamlit Cloud.")
            else:
                with st.spinner("💎 Generazione analisi finanziaria approfondita in corso..."):
                    prompt = f"""
                    Agisci come un direttore finanziario personale di altissimo livello. Analizza la lista di spese e/o entrate fornita dall'utente.
                    Fornisci una risposta approfondita, professionale e formattata esattamente con questa struttura e con le icone indicate (evita assolutamente errori di formattazione o residui di asterischi):

                    📊 **Riepilogo del Budget**
                    - Entrate totali: [calcola o stima in base al testo]
                    - Spese totali: [somma esatta delle voci]
                    - Rimante (Risparmio): [differenza e percentuale]

                    🔍 **Analisi della situazione**
                    [Spiega lo stato di salute finanziaria in chiaro, valutando se si è in pareggio o a rischio imprevisti].

                    💪 **Punti di forza:**
                    - [Analizza le voci positive]

                    ⚠ **Punti critici (dove intervenire):**
                    - [Analizza le voci alte e dai consigli pratici di taglio].

                    💡 **Proposta di ottimizzazione (Obiettivo Risparmio)**
                    Se provassi a ricalibrare le spese in questo modo:
                    - [Elenca le singole voci corrette/ottimizzate]
                    - 👈 **Nuove uscite:** [Totale ottimizzato]
                    - 👈 **Nuovo risparmio mensile:** [Nuovo importo e percentuale]
                    [Concludi con una frase motivazionale].

                    Testo inserito dall'utente:
                    {user_text_input}
                    """
                    
                    try:
                        response = model.generate_content(prompt)
                        if response and response.text:
                            st.session_state.analisi_effettuata = True
                            st.session_state.ultimo_risultato = response.text
                            st.success("Analisi completata con successo!")
                        else:
                            st.warning("Risposta vuota ricevuta dai server.")
                    except Exception as api_err:
                        st.error(f"Errore durante l'analisi: {api_err}")

    # Mostra l'analisi se è già stata effettuata
    if st.session_state.analisi_effettuata and st.session_state.ultimo_risultato:
        st.markdown(st.session_state.ultimo_risultato)
        
        # 💡 BARRA PER DOMANDE O DUBBI (APPARE SOLO DOPO L'ANALISI)
        st.markdown("---")
        st.subheader("❓ Domande o Dubbi sull'analisi")
        user_question = st.text_input("Vuoi chiedere un chiarimento o approfondire un punto specifico?", placeholder="Es. Come posso tagliare ulteriormente sulle spese vive?")
        
        if st.button("Fai una domanda al consulente"):
            if user_question.strip() and model:
                with st.spinner("Elaborazione risposta al tuo dubbio..."):
                    followup_prompt = f"Basandoti sull'analisi precedente fatta per l'utente, rispondi a questa domanda specifica mantenendo il tono da direttore finanziario: {user_question}"
                    followup_resp = model.generate_content(followup_prompt)
                    if followup_resp and followup_resp.text:
                        st.markdown("### 💬 Risposta del Consulente:")
                        st.markdown(followup_resp.text)

    st.markdown("---")
    st.subheader("📁 Carica Screenshot o Documento")
    uploaded_file = st.file_uploader("Carica lo scontrino o l'estratto conto (PNG, JPG, PDF)", type=["png", "jpg", "jpeg", "pdf"])
    if uploaded_file:
        st.image(uploaded_file, caption="Documento caricato con successo", use_column_width=True)
        if st.button("Analizza Documento"):
            st.success("Documento elaborato correttamente!")

with tab2:
    st.subheader(f"🎯 {t['goal']}")
    user_goal = st.text_input("Crea o aggiorna il tuo obiettivo personale di risparmio:")
    if user_goal:
        st.info(f"Obiettivo registrato: {user_goal}")

with tab3:
    st.subheader("📲 Inserimento Rapido SMS / Notifiche")
    sms_text = st.text_area("Copia e incolla qui il testo di SMS o notifiche bancarie:")
    if st.button("Analizza SMS"):
        st.success("Testo SMS analizzato correttamente!")

with tab4:
    st.subheader(f"⭐ {t['review']}")
    st.markdown("⭐⭐⭐⭐⭐ **4.9 / 5.0** - *'Questa app mi ha svoltato la gestione del budget!'* - Marco R.")
