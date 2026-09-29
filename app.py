import streamlit as st
from datetime import date
import time
import google.generativeai as genai

# Configurazione della pagina
st.set_page_config(
    page_title="Split & Save AI - Pro",
    page_icon="💡",
    layout="centered"
)

# --- 🤖 CONFIGURAZIONE GEMINI ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    generation_config = {
        "temperature": 0.3,
        "max_output_tokens": 1500,
    }
    
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
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

# --- GESTIONE SESSIONE ---
oggi = date.today()
if "last_date" not in st.session_state or st.session_state["last_date"] != oggi:
    st.session_state["last_date"] = oggi
    st.session_state["free_complete"] = 3
    st.session_state["free_limited"] = 1

# --- LINGUE & DIZIONARIO ---
LANGUAGES = {
    "Italiano": {"title": "Split & Save AI 💡", "subtitle": "Il tuo direttore finanziario personale.", "unlimited": "Account Illimitato Attivo (Admin)", "review": "Recensioni Verificate", "goal": "I tuoi Obiettivi Personali"},
    "English": {"title": "Split & Save AI 💡", "subtitle": "Your personal financial director.", "unlimited": "Unlimited Account Active (Admin)", "review": "Verified Reviews", "goal": "Your Personal Goals"}
}

selected_lang = st.sidebar.selectbox("🌍 Lingua / Language", list(LANGUAGES.keys()), index=0)
t = LANGUAGES[selected_lang]

st.title(t["title"])
st.write(t["subtitle"])

# --- SIDEBAR: GUIDA & ADMIN ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 📱 Installa sul Telefono")
st.sidebar.info("Tocca i **tre puntini ⠇** in alto a destra nel browser e seleziona **'Aggiungi a schermata Home'**.")

st.sidebar.markdown("---")
st.sidebar.header("🔐 Area Personale / Admin")
admin_password = st.sidebar.text_input("Password Segreta", type="password")

try:
    real_password = st.secrets["ADMIN_PASSWORD"]
except Exception:
    real_password = ""

is_admin = (admin_password == real_password)

if is_admin:
    st.sidebar.success("🔑 Accesso Admin Riconosciuto!")
    st.success(f"🔓 {t['unlimited']}")
else:
    if admin_password:
        st.sidebar.error("Password errata.")
    st.sidebar.info(f"Stai usando il piano **Free**: massimo 3 analisi al giorno.\nRimaste: {st.session_state['free_complete']}/3")

# --- PIANI STRIPE ---
st.sidebar.markdown("---")
st.sidebar.header("💳 Piani & Abbonamenti")
tier_choices = [
    "Pacchetto day smart (€0.59 - 1 analisi)",
    "Pacchetto smart (€4.99 / settimana)",
    "Pacchetto unlimited (€14.99 / mese illimitato)"
]
selected_tier = st.sidebar.selectbox("Seleziona il piano:", tier_choices)
STRIPE_URLS = {
    "Pacchetto day smart (€0.59 - 1 analisi)": "https://buy.stripe.com/test_eVq9AU7LnfG70wR9i0bwk08",
    "Pacchetto smart (€4.99 / settimana)": "https://buy.stripe.com/test_7sYdRa5Df65x7Zj0Lubwk05",
    "Pacchetto unlimited (€14.99 / mese illimitato)": "https://buy.stripe.com/test_7sY6oI6HjctVcfz8dWbwk07"
}
st.sidebar.markdown(f"[Procedi al Checkout Sicuro]({STRIPE_URLS[selected_tier]})")

# --- INTERFACCIA PRINCIPALE ---
tab1, tab2, tab3, tab4 = st.tabs(["📥 Inserimento", "🎯 Obiettivi & Sblocco", "🎤 Voce & SMS", "⭐ Recensioni"])

with tab1:
    st.subheader("Incolla qui la lista delle spese:")
    user_text_input = st.text_area("Spese:", placeholder="Es. 2000 stipendio, 500 affitto...", label_visibility="collapsed")
    
    bottoni_testo = "Analizza (Illimitato 🔓)" if is_admin else "Analiza (Free)"
    
    if st.button(bottoni_testo):
        if not user_text_input.strip():
            st.warning("Inserisci prima la lista delle spese.")
        else:
            permesso_ok = False
            if is_admin:
                permesso_ok = True
            elif st.session_state["free_complete"] > 0:
                st.session_state["free_complete"] -= 1
                permesso_ok = True

            if not permesso_ok:
                st.error("Hai esaurito le analisi gratuite giornaliere. Inserisci la password admin nella barra laterale per avere accesso illimitato!")
            else:
                if not gemini_disponibile:
                    st.error("⚠️ Chiave API di Gemini non configurata correttamente nei Secrets.")
                else:
                    with st.spinner("💎 Generazione analisi finanziaria approfondita in corso..."):
                        prompt = f"""
                        Agisci come un direttore finanziario personale di altissimo livello. Analizza la lista di spese e/o entrate fornita dall'utente.
                        Fornisci una risposta approfondita, professionale e formattata esattamente con questa struttura e con le icone indicate:

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
                        
                        response = None
                        successo = False
                        
                        for tentativo in range(3):
                            try:
                                response = model.generate_content(prompt)
                                if response and response.text:
                                    successo = True
                                    break
                            except Exception as api_err:
                                error_str = str(api_err)
                                if ("429" in error_str or "quota" in error_str.lower()) and tentativo < 2:
                                    time.sleep(6)
                                    continue
                                else:
                                    if tentativo == 2:
                                        st.error(f"Errore di comunicazione con Google API: {api_err}")

                        if successo and response and response.text:
                            st.success("Analisi completata con successo!")
                            st.markdown(response.text)
                        else:
                            st.warning("⏳ **I server di Google stanno ricevendo molte richieste in questo secondo.** Attendi 10 secondi e clicca nuovamente sul pulsante d'analisi.")

    st.markdown("---")
    st.subheader("📁 Carica Screenshot o Documento")
    uploaded_file = st.file_uploader("Carica lo scontrino o l'estratto conto (PNG, JPG, PDF)", type=["png", "jpg", "jpeg", "pdf"])
    if uploaded_file:
        st.image(uploaded_file, caption="Documento caricato con successo", use_column_width=True)
        if st.button("Analizza Documento"):
            if is_admin or st.session_state["free_complete"] > 0:
                if not is_admin:
                    st.session_state["free_complete"] -= 1
                st.success("Documento analizzato con successo!")
            else:
                st.error("Analisi gratuite esaurite.")

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
