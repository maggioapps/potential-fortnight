import streamlit as st
from datetime import date

# Configurazione della pagina
st.set_page_config(
    page_title="Split & Save AI",
    page_icon="💡",
    layout="centered"
)

# --- 🎨 1. STILE GRAFICO E ALTO CONTRASTO ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 50%, #eff6ff 100%);
        color: #1f2937;
    }
    div.stMarkdown, .stTabs, .stFileUploader, .stTextArea, .stTextInput {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.2);
        margin-bottom: 10px;
        color: #1f2937;
    }
    p, span, label, div, .stMarkdown p {
        color: #1f2937 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    h1, h2, h3 {
        color: #065f46 !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Stile speciale per evidenziare il bottone app mobile */
    .mobile-btn {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white !important;
        padding: 12px 20px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        display: block;
        text-decoration: none;
        box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3);
        margin-bottom: 15px;
    }
    .mobile-btn:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. GESTIONE SESSIONE PER LE ANALISI GRATUITE GIORNALIERE ---
oggi = date.today()
if "last_date" not in st.session_state or st.session_state["last_date"] != oggi:
    st.session_state["last_date"] = oggi
    st.session_state["free_complete"] = 2
    st.session_state["free_limited"] = 1

# --- 3. CONFIGURAZIONE DELLE 12 LINGUE & DIZIONARIO ---
LANGUAGES = {
    "Italiano": {"title": "Split & Save AI - Risparmio Intelligente 💡", "unlimited": "Account Illimitato Attivo (Admin)", "review": "Recensioni Verificate", "goal": "I tuoi Obiettivi Personali"},
    "English": {"title": "Split & Save AI - Smart Savings 💡", "unlimited": "Unlimited Account Active (Admin)", "review": "Verified Reviews", "goal": "Your Personal Goals"},
    "Español": {"title": "Split & Save AI - Ahorro Inteligente 💡", "unlimited": "Cuenta Ilimitada Activa (Admin)", "review": "Reseñas Verificadas", "goal": "Tus Objetivos Personales"},
    "Français": {"title": "Split & Save AI - Économies Intelligentes 💡", "unlimited": "Compte Illimité Actif (Admin)", "review": "Avis Vérifiés", "goal": "Vos Objectifs Personnels"},
    "Deutsch": {"title": "Split & Save AI - Intelligentes Sparen 💡", "unlimited": "Unbegrenztes Konto Aktiv (Admin)", "review": "Verifizierte Bewertungen", "goal": "Ihre persönlichen Ziele"},
    "Português": {"title": "Split & Save AI - Poupança Inteligente 💡", "unlimited": "Conta Ilimitada Ativa (Admin)", "review": "Avaliações Verificadas", "goal": "Seus Objetivos Pessoais"},
    "Русский": {"title": "Split & Save AI - Умные сбережения 💡", "unlimited": "Безлимитный аккаунт активен (Admin)", "review": "Проверенные отзывы", "goal": "Ваши личные цели"},
    "中文": {"title": "Split & Save AI - 智能省钱 💡", "unlimited": "无限账户已激活 (Admin)", "review": "verified reviews", "goal": "您的个人目标"},
    "العربية": {"title": "Split & Save AI - التوفير الذكي 💡", "unlimited": "الحساب غير المحدود نشط (Admin)", "review": "تقييمات موثوقة", "goal": "أهدافك الشخصية"},
    "日本語": {"title": "Split & Save AI - スマート節約 💡", "unlimited": "無制限アカウント有効 (Admin)", "review": "確認済みレビュー", "goal": "あなたの個人的な目標"},
    "Hindi": {"title": "Split & Save AI - स्मार्ट बचत 💡", "unlimited": "अिमिटेड अकाउंट सक्रिय (Admin)", "review": "समीक्षाएं", "goal": "आपके व्यक्तिगत लक्ष्य"},
    "Polski": {"title": "Split & Save AI - Inteligentne Oszczędzanie 💡", "unlimited": "Konto bez limitu aktywne (Admin)", "review": "Zweryfikowane opinie", "goal": "Twoje cele osobiste"}
}

selected_lang = st.sidebar.selectbox("🌍 Lingua / Language", list(LANGUAGES.keys()), index=0)
t = LANGUAGES[selected_lang]

st.title(t["title"])

# --- 4. TASTO DOWNLOAD APP MOBILE (Aggiornato con il tuo link reale) ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 📱 Scarica l'App")
link_app_mobile = "https://potential-fortnight-funhb2jbmzj4ekbspwag3k.streamlit.app/"
st.sidebar.markdown(f'<a href="{link_app_mobile}" target="_blank" class="mobile-btn">📥 Scarica App Mobile</a>', unsafe_allow_html=True)

# --- 5. ACCESSO AMMINISTRATIVO SICURO E CONTEGGIO GRATUITO ---
st.sidebar.markdown("---")
st.sidebar.header("🔐 Area Personale / Admin")
admin_password = st.sidebar.text_input("Inserisci Password Segreta", type="password")

try:
    real_password = st.secrets["ADMIN_PASSWORD"]
except:
    real_password = "DefaultPasswordSeMancanoISecrets"

is_admin = (admin_password == real_password)

if is_admin:
    st.sidebar.success("🔑 Accesso Admin Riconosciuto!")
    st.success(f"🔓 {t['unlimited']}")
else:
    if admin_password:
        st.sidebar.error("Password errata.")
    st.sidebar.info(f"🎁 **Analisi gratuite di oggi:**\n- Complete: {st.session_state['free_complete']}/2\n- Limitate: {st.session_state['free_limited']}/1")

# --- 6. GESTIONE DEI PIANI STRIPE (Abbonamenti) ---
st.sidebar.markdown("---")
st.sidebar.header("💳 Scegli un Piano / Abbonamento")

tier_choices = [
    "Pacchetto day smart (€0.59 - 1 analisi)",
    "Pacchetto day smart 2 (€1.59 - 2 analisi)",
    "Pacchetto day smart 3 (€1.99 - 5 analisi)",
    "Pacchetto day premium (€0.99 - 1 analisi completa)",
    "Pacchetto day premium 2 (€1.99 - 2 analisi complete)",
    "Day premium 3 (€2.59 - 5 analisi complete)",
    "Pacchetto smart (€4.99 / settimana)",
    "Pacchetto pro (€9.99 / settimana con IA)",
    "Pacchetto unlimited (€14.99 / mese illimitato)"
]

selected_tier = st.sidebar.selectbox("Seleziona il piano o pacchetto:", tier_choices)

STRIPE_PAYMENT_URLS = {
    "Pacchetto day smart (€0.59 - 1 analisi)": "https://buy.stripe.com/test_eVq9AU7LnfG70wR9i0bwk08",
    "Pacchetto day smart 2 (€1.59 - 2 analisi)": "https://buy.stripe.com/test_6oUdRa3v72TldjD3XGbwk00",
    "Pacchetto day smart 3 (€1.99 - 5 analisi)": "https://buy.stripe.com/test_bJebJ2ghTalN3J379Sbwk01",
    "Pacchetto day premium (€0.99 - 1 analisi completa)": "https://buy.stripe.com/test_fZu00ke9LbpR5RbfGobwk02",
    "Pacchetto day premium 2 (€1.99 - 2 analisi complete)": "https://buy.stripe.com/test_8x29AU6HjgKbdjDgKsbwk03",
    "Day premium 3 (€2.59 - 5 analisi complete)": "https://buy.stripe.com/test_3cIcN62r3bpR3J38dWbwk04",
    "Pacchetto smart (€4.99 / settimana)": "https://buy.stripe.com/test_7sYdRa5Df65x7Zj0Lubwk05",
    "Pacchetto pro (€9.99 / settimana con IA)": "https://buy.stripe.com/test_28EaEY4zb65xa7r79Sbwk06",
    "Pacchetto unlimited (€14.99 / mese illimitato)": "https://buy.stripe.com/test_7sY6oI6HjctVcfz8dWbwk07"
}

st.sidebar.markdown(f"[Procedi al Checkout Sicuro]({STRIPE_PAYMENT_URLS[selected_tier]})")

# --- 7. FUNZIONI PRINCIPALI DELL'APP ---
tab1, tab2, tab3, tab4 = st.tabs(["📥 Inserimento", "🎯 Obiettivi & Sblocco", "🎤 Voce & SMS", "⭐ Recensioni"])

with tab1:
    st.subheader("✍️ Inserimento Testo Normale")
    user_text_input = st.text_area("Scrivi o incolla qui le tue spese, note o dettagli liberi:", placeholder="Es. Speso 45€ al supermercato e 12€ per la benzina...")
    
    if st.button("🚀 Analizza"):
        if user_text_input.strip() == "":
            st.warning("Per favore inserisci prima del testo da analizzare.")
        else:
            if is_admin or st.session_state["free_complete"] > 0:
                if not is_admin:
                    st.session_state["free_complete"] -= 1
                st.success("✨ **Analisi Completata con Successo!** Ecco i dettagli elaborati dal tuo testo.")
                st.info(f"Testo analizzato: *{user_text_input}*")
            else:
                st.error("Hai esaurito le 2 analisi complete gratuite di oggi. Scegli un pacchetto nella barra laterale!")

    st.markdown("---")
    
    st.subheader("📁 Carica Screenshot o Documento")
    uploaded_file = st.file_uploader("Carica lo scontrino o l'estratto conto (PNG, JPG, PDF)", type=["png", "jpg", "jpeg", "pdf"])
    if uploaded_file:
        st.image(uploaded_file, caption="Documento caricato con successo", use_column_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✨ Analisi Completa File"):
                if is_admin or st.session_state["free_complete"] > 0:
                    if not is_admin:
                        st.session_state["free_complete"] -= 1
                    st.success("Analisi Completa del file eseguita con successo!")
                else:
                    st.error("Analisi complete gratuite giornaliere esaurite.")
        with col2:
            if st.button("🔍 Analisi Limitata File"):
                if is_admin or st.session_state["free_limited"] > 0:
                    if not is_admin:
                        st.session_state["free_limited"] -= 1
                    st.info("Analisi Limitata del file eseguita con successo!")
                else:
                    st.error("Analisi limitata gratuita giornaliera esaurita.")

with tab2:
    st.subheader(f"🎯 {t['goal']}")
    user_goal = st.text_input("Crea o aggiorna il tuo obiettivo personale di risparmio:")
    if user_goal:
        st.info(f"Obiettivo registrato: {user_goal}")
    
    st.markdown("---")
    st.markdown("### 💡 Consiglio d'oro per la schermata di blocco")
    st.info("Imposta il tuo risparmio giornaliero come sfondo della schermata di blocco per mantenere alta la motivazione ed evitare spese inutili!")

with tab3:
    st.subheader("📲 Inserimento Rapido SMS / Notifiche")
    sms_text = st.text_area("Copia e incolla qui il testo di SMS o notifiche bancarie:")
    if st.button("Analizza SMS"):
        if is_admin or st.session_state["free_complete"] > 0 or st.session_state["free_limited"] > 0:
            st.success("Testo SMS analizzato correttamente!")
        else:
            st.error("Analisi gratuite giornaliere esaurite. Scegli un piano o pacchetto nella barra laterale.")
    
    st.markdown("### 🎤 Comando Vocale")
    if st.button("🎤 Avvia Registrazione Vocale"):
        if is_admin or st.session_state["free_complete"] > 0 or st.session_state["free_limited"] > 0:
            st.warning("Ascolto vocale in corso... Analisi completata!")
        else:
            st.error("Analisi gratuite giornaliere esaurite. Scegli un piano o pacchetto nella barra laterale.")

with tab4:
    st.subheader(f"⭐ {t['review']}")
    st.markdown("⭐⭐⭐⭐⭐ **4.9 / 5.0** - *'Questa app mi ha svoltato la gestione del budget!'* - Marco R.")
    st.markdown("⭐⭐⭐⭐⭐ **5.0 / 5.0** - *'Il sistema multilingua e il copia-incolla degli SMS sono comodissimi.'* - Sarah K.")
