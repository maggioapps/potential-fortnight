import streamlit as st
import google.generativeai as genai
import io
import pypdf
from PIL import Image
import pandas as pd
import plotly.express as px
import random

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
            model_name='gemini-1.5-flash',
            generation_config={"temperature": 0.8, "max_output_tokens": 2048}
        )
        gemini_disponibile = True
except Exception:
    gemini_disponibile = False

# Stile grafico avanzato e ottimizzato per Mobile
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 50%, #eff6ff 100%);
    }
    div.stMarkdown, .stTabs, .stFileUploader, .stTextArea, .stTextInput {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 14px;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.2);
        margin-bottom: 10px;
    }
    h1, h2, h3 {
        color: #065f46 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Split & Save AI 💡")
st.write("Il tuo direttore finanziario personale, cinico ma saggio.")

# --- GESTIONE STATO UTENTE E VISITE PERSISTENTI ---
if "is_loggato" not in st.session_state:
    st.session_state.is_loggato = False
if "utente_email" not in st.session_state:
    st.session_state.utente_email = ""
if "storico_salvataggi" not in st.session_state:
    st.session_state.storico_salvataggi = []
if "notifiche_attive" not in st.session_state:
    st.session_state.notifiche_attive = False

if "visitato" not in st.session_state:
    st.session_state.visitato = True
    if "visite" not in st.session_state:
        st.session_state.visite = 142
    else:
        st.session_state.visite += 1
else:
    if "visite" not in st.session_state:
        st.session_state.visite = 142

if "conteggio_usi" not in st.session_state:
    st.session_state.conteggio_usi = 0
if "analisi_fatta" not in st.session_state:
    st.session_state.analisi_fatta = False
if "testo_risultato" not in st.session_state:
    st.session_state.testo_risultato = ""
if "ultimo_insulto" not in st.session_state:
    st.session_state.ultimo_insulto = ""
if "recensioni" not in st.session_state:
    st.session_state.recensioni = [
        ("Marco R.", "⭐⭐⭐⭐⭐", "App fantastica!"),
        ("Giulia V.", "⭐⭐⭐⭐⭐", "Molto utile per risparmiare.")
    ]

st.sidebar.markdown("### 👤 Accesso & Account")

if not st.session_state.is_loggato:
    scelta_accesso = st.sidebar.radio("Scegli modalità:", ["Ospite (Senza registrazione)", "Accedi / Registrati Gratis"])
    
    if scelta_accesso == "Accedi / Registrati Gratis":
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔐 Auth Account")
        input_user = st.sidebar.text_input("Email o Nome Utente:", placeholder="es. mario_rossi")
        input_pass = st.sidebar.text_input("Password:", type="password", placeholder="••••••••")
        
        col_reg1, col_reg2 = st.sidebar.columns(2)
        with col_reg1:
            if st.button("Registrati"):
                if input_user and input_pass:
                    st.session_state.is_loggato = True
                    st.session_state.utente_email = input_user
                    st.success("Account creato!")
                    st.rerun()
                else:
                    st.warning("Inserisci credenziali.")
        with col_reg2:
            if st.button("Login"):
                if input_user and input_pass:
                    st.session_state.is_loggato = True
                    st.session_state.utente_email = input_user
                    st.success("Accesso effettuato!")
                    st.rerun()
                else:
                    st.warning("Inserisci credenziali.")
    else:
        st.sidebar.info("🔓 **Modalità Ospite attiva**")
else:
    st.sidebar.success(f"Benvenuto, **{st.session_state.utente_email}**! 🔒")
    notifiche_push = st.sidebar.toggle("🔔 Notifiche Push", value=st.session_state.notifiche_attive)
    st.session_state.notifiche_attive = notifiche_push
        
    if st.sidebar.button("🚪 Esci (Logout)"):
        st.session_state.is_loggato = False
        st.session_state.utente_email = ""
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌍 Selezione Lingua")
lista_lingue = [
    "Rilevamento Automatico (Auto)",
    "Italiano", "English", "Español", "Français", "Deutsch", 
    "Português", "Română", "العربية", "中文", "हिन्दी", 
    "日本語", "Русский", "Polski", "Nederlands", "Ελληνικά", 
    "Türkçe", "Українська", "Magyar", "Čeština", "Svenska", "한국어"
]
lingua_selezionata = st.sidebar.selectbox("Scegli la lingua:", lista_lingue)

# --- MENU DI NAVIGAZIONE A TENDINA (OTTIMIZZATO PER MOBILE) ---
st.markdown("### 📌 Seleziona Sezione")
opzioni_menu = [
    "📥 Inserimento txt (Spese/Entrate)", 
    "📁 Importa File & Foto", 
    "🎤 Voce & SMS / Notifiche", 
    "🎯 Obiettivi di Risparmio", 
    "🔥 Generatore Insulti & Reazioni",
    "⭐ Commenti & Statistiche"
]
if st.session_state.is_loggato:
    opzioni_menu.insert(5, "📂 Storico Cloud")

scelta_sezione = st.selectbox("Scegli cosa fare:", opzioni_menu, label_visibility="collapsed")

# Funzione centrale di analisi
def esegui_analisi_ia_profonda(contenuto_input, titolo_sorgente="Dati utente", is_image=False, image_obj=None, is_obiettivo=False):
    if not gemini_disponibile or not model:
        st.error("⚠ Configurazione API non rilevata o modello non disponibile. Controlla la chiave nei Secrets.")
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
            Agisci come un consulente finanziario cinico ma saggio. L'utente ha inserito questo obiettivo: '{contenuto_input}'.
            Fornisci un'analisi tagliente ma costruttiva, rispettando la sensibilità della persona.
            
            Usa questa struttura esatta:
            📢 **Giudizio del Direttore sull'Obiettivo**
            🎯 **Fattibilità & Analisi**
            ⚠ **Ostacoli Critici**
            💡 **Consiglio Mirato**
            """
        else:
            prompt = f"""
            {istruzione_lingua}
            Agisci come un direttore finanziario cinico ma attento alla fragilità emotiva dell'utente. Analizza i dati: {titolo_sorgente}.
            Cita voci specifiche con ironia tagliente, senza però risultare crudele.
            
            Usa questa struttura esatta:
            📢 **Giudizio del Direttore**
            📊 **Riepilogo Numerico & Budget** [Entrate, Uscite, Saldo e Margine]
            🔍 **Analisi Dettagliata** [Transazioni specifiche]
            💡 **Consiglio Mirato** [Azioni precise]
            🏆 **Badge & Voto del Mese**: [Voto da A+ a F e titolo ironico]
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
                
                if st.session_state.is_loggato:
                    st.session_state.storico_salvataggi.insert(0, {
                        "titolo": titolo_sorgente,
                        "risultato": response.text
                    })
                    if st.session_state.notifiche_attive:
                        st.sidebar.toast("📲 Notifica push inviata!", icon="🔥")
                
                st.success("Analisi completata!")
        except Exception as e:
            st.error(f"Errore durante l'analisi IA: {e}")

def mostra_grafico_compatto():
    st.markdown("### 📊 Ripartizione Categorie")
    dati_grafico = pd.DataFrame({
        'Categoria': ['Casa / Affitto', 'Cibo & Spesa', 'Svago / Extra', 'Risparmio'],
        'Importo (€)': [600, 350, 250, 150]
    })
    fig = px.pie(
        dati_grafico, 
        names='Categoria', 
        values='Importo (€)', 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        height=220,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)

# --- GESTIONE DELLE SEZIONI CON IL MENU A TENDINA ---

if scelta_sezione == "📥 Inserimento txt (Spese/Entrate)":
    st.subheader("Incolla qui la lista delle spese e delle entrate:")
    user_text_input = st.text_area("Movimenti:", placeholder="Es. +2500 stipendio, -500 affitto...", label_visibility="collapsed")
    
    if st.button("Analizza Movimenti"):
        if not user_text_input.strip():
            st.warning("Inserisci prima i movimenti finanziari.")
        else:
            esegui_analisi_ia_profonda(user_text_input, "Lista testuale Entrate/Uscite")

    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        mostra_grafico_compatto()
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)

elif scelta_sezione == "📁 Importa File & Foto":
    st.subheader("📁 Importa File & 📷 Foto (PDF, TXT, CSV, JPG, PNG)")
    uploaded_file = st.file_uploader("Carica file o foto", type=["pdf", "txt", "csv", "jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        file_name_lower = uploaded_file.name.lower()
        is_img_file = file_name_lower.endswith(('.jpg', '.jpeg', '.png'))
        
        if is_img_file:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"Foto: {uploaded_file.name}", use_container_width=True)
        else:
            st.success(f"File caricato: **{uploaded_file.name}**")
        
        if st.button("🚀 Avvia Analisi Avanzata"):
            try:
                bytes_data = uploaded_file.getvalue()
                if is_img_file:
                    image_obj = Image.open(io.BytesIO(bytes_data))
                    esegui_analisi_ia_profonda("", f"Foto documento: {uploaded_file.name}", is_image=True, image_obj=image_obj)
                    st.rerun()
                elif file_name_lower.endswith('.pdf'):
                    pdf_file_obj = io.BytesIO(bytes_data)
                    reader = pypdf.PdfReader(pdf_file_obj)
                    extracted_pages = [page.extract_text() for page in reader.pages if page.extract_text()]
                    testo_estratto = "\n".join(extracted_pages) or "PDF vuoto."
                    esegui_analisi_ia_profonda(testo_estratto[:30000], f"PDF: {uploaded_file.name}")
                    st.rerun()
                else:
                    testo_estratto = bytes_data.decode("utf-8", errors="ignore")
                    esegui_analisi_ia_profonda(testo_estratto[:30000], f"Documento: {uploaded_file.name}")
                    st.rerun()
            except Exception as e:
                st.error(f"Errore: {e}")

    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        mostra_grafico_compatto()
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)

elif scelta_sezione == "🎤 Voce & SMS / Notifiche":
    st.subheader("🎤 Notifiche Bancarie (Entrate & Uscite)")
    sms_voce_input = st.text_area("Testo notifica:", placeholder="Es. 'Bonifico +1850€'...")
    
    if st.button("Analizza Notifica"):
        if not sms_voce_input.strip():
            st.warning("Inserisci il testo.")
        else:
            esegui_analisi_ia_profonda(sms_voce_input, "Notifica Bancaria")

    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        mostra_grafico_compatto()
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)

elif scelta_sezione == "🎯 Obiettivi di Risparmio":
    st.subheader("🎯 Obiettivi Personali")
    obiettivo_input = st.text_input("Descrivi l'obiettivo:", placeholder="Es. Risparmiare 3000 euro per vacanza.")
    
    if st.button("Genera Piano Strategico"):
        if not obiettivo_input.strip():
            st.warning("Inserisci l'obiettivo.")
        else:
            esegui_analisi_ia_profonda(obiettivo_input, "Obiettivo di Risparmio", is_obiettivo=True)

    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)

elif scelta_sezione == "🔥 Generatore Insulti & Reazioni":
    st.subheader("🔥 Generatore Insulti & Reazioni")
    st.info("Scegli la situazione o prova a provocare il sistema. Se rispondi male o sfotti, il Direttore distruggerà le argomentazioni tenendo conto del tuo umore.")
    
    modalita_input = st.radio("Modalità:", ["Situazione critica", "Voglio provocare il sistema 😈"])
    
    if modalita_input == "Situazione critica":
        situazione_scelta = st.selectbox("Situazione:", [
            "Conto in rosso prima di fine mese",
            "Speso tutto in aperitivi e ristoranti",
            "Compro cianfrusaglie su Amazon",
            "Zero risparmi e vivo alla giornata"
        ])
        input_provocazione = ""
    else:
        input_provocazione = st.text_input("La tua provocazione:", placeholder="Es. Ma che ne capisci tu...")
        situazione_scelta = ""

    umore_utente = st.select_slider(
        "Come ti senti oggi emotivamente?",
        options=["Fragile / Ho bisogno di tatto 🥺", "Equilibrato 🙂", "Pronto alla battaglia / Distruggimi 🥊"],
        value="Equilibrato 🙂"
    )

    if st.button("💥 Esegui Verdetto Insulto"):
        if model:
            with st.spinner("Il Direttore sta riflettendo..."):
                tocco_sensibilita = ""
                if "Fragile" in umore_utente:
                    tocco_sensibilita = "L'utente è fragile oggi. Sii spiritoso ma dolce e costruttivo, senza ferire."
                elif "Equilibrato" in umore_utente:
                    tocco_sensibilita = "Usa ironia tagliente ma rispettosa."
                else:
                    tocco_sensibilita = "L'utente sta provocando. Distruggi le scuse con sarcasmo devastante e umorismo nero!"

                if modalita_input == "Voglio provocare il sistema 😈" and input_provocazione.strip():
                    prompt_insulto = f"{tocco_sensibilita}\nL'utente ha detto: '{input_provocazione}'. Demolisci la provocazione con superiorità logica e cinismo."
                else:
                    prompt_insulto = f"{tocco_sensibilita}\nL'utente si trova qui: '{situazione_scelta}'. Genera un verdetto ironico e mirato."

                try:
                    res_insulto = model.generate_content(prompt_insulto)
                    if res_insulto and res_insulto.text:
                        st.session_state.ultimo_insulto = res_insulto.text
                except Exception as e:
                    st.session_state.ultimo_insulto = f"Errore: {e}"
        else:
            st.session_state.ultimo_insulto = "Configurazione API non attiva."
            
    if st.session_state.ultimo_insulto:
        st.markdown("---")
        st.error(f"### 🛑 Verdetto:\n\n{st.session_state.ultimo_insulto}")

elif scelta_sezione == "📂 Storico Cloud" and st.session_state.is_loggato:
    st.subheader("📂 Storico Cloud & Automazioni")
    if not st.session_state.storico_salvataggi:
        st.info("Nessun report salvato.")
    else:
        for idx, item in enumerate(st.session_state.storico_salvataggi):
            with st.expander(f"Report #{len(st.session_state.storico_salvataggi) - idx} - {item['titolo']}"):
                st.markdown(item['risultato'])

elif scelta_sezione == "⭐ Commenti & Statistiche":
    st.subheader("📊 Statistiche App")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="👥 Visite", value=st.session_state.visite)
    with col2:
        st.metric(label="🚀 Analisi", value=st.session_state.conteggio_usi)

    st.markdown("---")
    st.subheader("⭐ Lascia un Commento")
    nome_u = st.text_input("Nome:", key="rec_nome")
    stelle_u = st.selectbox("Stelle:", ["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐", "⭐"], key="rec_stelle")
    testo_u = st.text_area("Commento:", key="rec_testo")
    
    if st.button("Invia Commento Community"):
        if nome_u.strip() and testo_u.strip():
            st.session_state.recensioni.insert(0, (nome_u, stelle_u, testo_u))
            st.success("Grazie per il commento!")
        else:
            st.warning("Compila tutti i campi.")
            
    st.markdown("---")
    st.subheader("📋 Community")
    for ut, st_val, comm in st.session_state.recensioni:
        st.markdown(f"**{ut}** - {st_val}\n\n*{comm}*")
        st.markdown("---")
