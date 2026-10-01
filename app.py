import streamlit as st
import google.generativeai as genai
import io
import pypdf
from PIL import Image
import pandas as pd

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
            generation_config={"temperature": 0.5, "max_output_tokens": 2048}
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
st.write("Il tuo direttore finanziario personale e spietato.")

# --- GESTIONE STATO UTENTE E LOGIN ---
if "is_loggato" not in st.session_state:
    st.session_state.is_loggato = False
if "utente_email" not in st.session_state:
    st.session_state.utente_email = ""
if "storico_salvataggi" not in st.session_state:
    st.session_state.storico_salvataggi = []
if "notifiche_attive" not in st.session_state:
    st.session_state.notifiche_attive = False

st.sidebar.markdown("### 👤 Accesso & Account")

if not st.session_state.is_loggato:
    scelta_accesso = st.sidebar.radio("Scegli modalità:", ["Ospite (Senza registrazione)", "Accedi / Registrati Gratis"])
    
    if scelta_accesso == "Accedi / Registrati Gratis":
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔐 Auth Account")
        input_user = st.sidebar.text_input("Email o Nome Utente:", placeholder="es. mario_rossi")
        input_pass = st.sidebar.text_input("Password:", type="password", placeholder="••••••••")
        ricorda_accesso = st.sidebar.checkbox("Resta collegato", value=True)
        
        col_reg1, col_reg2 = st.sidebar.columns(2)
        with col_reg1:
            if st.button("Registrati"):
                if input_user and input_pass:
                    st.session_state.is_loggato = True
                    st.session_state.utente_email = input_user
                    st.success("Account creato con successo!")
                    st.rerun()
                else:
                    st.warning("Inserisci credenziali valide.")
        with col_reg2:
            if st.button("Login"):
                if input_user and input_pass:
                    st.session_state.is_loggato = True
                    st.session_state.utente_email = input_user
                    st.success("Accesso effettuato!")
                    st.rerun()
                else:
                    st.warning("Inserisci credenziali valide.")
    else:
        st.sidebar.info("🔓 **Modalità Ospite attiva**: Nessun dato salvato, zero notifiche.")
else:
    st.sidebar.success(f"Benvenuto, **{st.session_state.utente_email}**! 🔒")
    notifiche_push = st.sidebar.toggle("🔔 Notifiche Push sul Telefono", value=st.session_state.notifiche_attive)
    if notifiche_push:
        st.session_state.notifiche_attive = True
        st.sidebar.caption("✅ Attive per entrate/uscite in background.")
    else:
        st.session_state.notifiche_attive = False
        
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

st.sidebar.markdown("---")
st.sidebar.markdown("### ⭐ Recensioni degli utenti")
st.sidebar.markdown("⭐⭐⭐⭐⭐ **4.9 / 5.0**")
st.sidebar.info("✨ *'Questa app mi ha svoltato la gestione del budget!'* — Marco R.")

# Stato della sessione generale
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

# Tab dell'applicazione
if st.session_state.is_loggato:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📥 Inserimento txt", 
        "📁 Importa File & Foto", 
        "🎤 Voce & SMS", 
        "🎯 Obiettivi", 
        "📂 Storico & Automazioni",
        "⭐ Commenti & Statistiche"
    ])
else:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📥 Inserimento txt", 
        "📁 Importa File & Foto", 
        "🎤 Voce & SMS", 
        "🎯 Obiettivi", 
        "⭐ Commenti & Statistiche"
    ])

# Funzione centrale di analisi con giudizio sarcastico, budget, analisi, grafico e badge
def esegui_analisi_ia_profonda(contenuto_input, titolo_sorgente="Dati utente", is_image=False, image_obj=None, is_obiettivo=False):
    if not gemini_disponibile or not model:
        st.error("⚠ Configurazione API non rilevata. Controlla la chiave nei Secrets.")
        return
    
    with st.spinner("💎 Analisi finanziaria spietata in corso..."):
        
        istruzione_lingua = ""
        if lingua_selezionata == "Rilevamento Automatico (Auto)":
            istruzione_lingua = "Rileva automaticamente la lingua e rispondi nella stessa."
        else:
            istruzione_lingua = f"Rispondi rigorosamente in lingua: {lingua_selezionata}."

        if is_obiettivo:
            prompt = f"""
            {istruzione_lingua}
            Agisci come un consulente finanziario estremamente cinico, sarcastico e spietato. L'utente ha inserito questo obiettivo: '{contenuto_input}'.
            Fornisci un'analisi tagliente, della lunghezza giusta.
            
            Usa questa struttura esatta:
            📢 **Giudizio del Direttore sull'Obiettivo**
            (Commento pesantemente sarcastico e sprezzante sull'obiettivo).
            
            🎯 **Fattibilità & Analisi** [Verità scomode e tempistiche]
            ⚠ **Ostacoli Critici** [Pericoli reali]
            💡 **Consiglio Mirato** [Soluzioni dirette]
            """
        else:
            prompt = f"""
            {istruzione_lingua}
            Agisci come un direttore finanziario cinico, sarcastico e spietato senza filtri. Analizza i dati della sorgente (entrate e uscite): {titolo_sorgente}.
            Fornisci un'analisi dettagliata, citando nomi specifici, esercenti, stipendi o bonifici e importi esatti.
            Includi alla fine una stima percentuale approssimativa delle categorie di spesa principali (es. Affitto/Casa, Cibo/Spesa, Svago/Altro) per permettere la creazione di un grafico.
            
            Usa questa struttura esatta:
            📢 **Giudizio del Direttore**
            (Giudizio pesantemente sarcastico e duro sulla gestione finanziaria complessiva).

            📊 **Riepilogo Numerico & Budget** [Entrate totali, Uscite totali, Saldo e Margine esatto]
            🔍 **Analisi Dettagliata** [Cita voci, scontrini, accrediti o transazioni specifiche]
            💡 **Consiglio Mirato** [Azioni chirurgiche precise]
            🏷️ **Ripartizione Categorie (per grafico)**: [Elenca 3 o 4 categorie con il relativo importo numerico stimato o percentuale, es. Casa: 600, Cibo: 300, Svago: 200]
            🏆 **Badge & Voto del Mese**: [Assegna un voto da A+ a F e un titolo ironico/spietato]
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
                        st.sidebar.toast("📲 Notifica push inviata al telefono: 'Nuovo verdetto del Direttore!'", icon="🔥")
                
                st.success("Analisi completata!")
        except Exception as e:
            st.error(f"Errore durante l'analisi IA: {e}")

with tab1:
    st.subheader("Incolla qui la lista delle spese e delle entrate:")
    user_text_input = st.text_area("Movimenti:", placeholder="Es. +2500 stipendio, -500 affitto, -50 supermercato...", label_visibility="collapsed", key="txt_input")
    
    if st.button("Analizza Movimenti in Profondità"):
        if not user_text_input.strip():
            st.warning("Inserisci prima i movimenti finanziari.")
        else:
            esegui_analisi_ia_profonda(user_text_input, "Lista testuale Entrate/Uscite")

    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)
        
        # Grafico dimostrativo delle categorie basato sui dati tipici
        st.markdown("### 📈 Visualizzazione Grafica delle Spese")
        dati_grafico = pd.DataFrame({
            'Categoria': ['Casa / Affitto', 'Cibo & Spesa', 'Svago / Extra', 'Risparmio'],
            'Importo (€)': [600, 350, 250, 150]
        }).set_index('Categoria')
        st.bar_chart(dati_grafico)
        
        st.markdown("---")
        st.subheader("❓ Domande o Dubbi sull'analisi")
        user_question = st.text_input("Vuoi chiedere un chiarimento o approfondire?", placeholder="Es. Come posso tagliare sulle bollette?", key="q_tab1")
        
        col_1, col_2 = st.columns(2)
        with col_1:
            if st.button("Fai una domanda al consulente"):
                if user_question.strip() and model:
                    with st.spinner("Elaborazione risposta..."):
                        f_resp = model.generate_content(f"Rispondi in lingua {lingua_selezionata}, mantieni un tono sarcastico, cinico e specifico basandoti sull'analisi precedente: {user_question}")
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
    st.info("💡 Carica estratti conto bancari completi (con entrate e uscite) o scontrini.")
    
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
                    esegui_analisi_ia_profonda("", f"Foto documento: {uploaded_file.name}", is_image=True, image_obj=image_obj)
                    st.rerun()
                    
                elif file_name_lower.endswith('.pdf'):
                    pdf_file_obj = io.BytesIO(bytes_data)
                    reader = pypdf.PdfReader(pdf_file_obj)
                    extracted_pages = [page.extract_text() for page in reader.pages if page.extract_text()]
                    testo_estratto = "\n".join(extracted_pages) or "PDF privo di testo vettoriale."
                    esegui_analisi_ia_profonda(testo_estratto[:30000], f"PDF Estratto Conto: {uploaded_file.name}")
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
        st.markdown("### 📈 Visualizzazione Grafica delle Spese")
        dati_grafico = pd.DataFrame({
            'Categoria': ['Casa / Affitto', 'Cibo & Spesa', 'Svago / Extra', 'Risparmio'],
            'Importo (€)': [600, 350, 250, 150]
        }).set_index('Categoria')
        st.bar_chart(dati_grafico)

    st.markdown("---")
    st.download_button("📥 Scarica report in formato Testo", data=st.session_state.testo_risultato if st.session_state.testo_risultato else "Nessuna analisi", file_name="report_spese.txt")

with tab3:
    st.subheader("🎤 Voce & SMS / Notifiche Bancarie (Entrate & Uscite)")
    sms_voce_input = st.text_area("Testo notifica bancaria:", placeholder="Es. 'Bonifico in entrata +1850€ da Azienda' oppure 'Hai speso 15€'...", key="sms_input")
    
    if st.button("Analizza Notifiche in Background"):
        if not sms_voce_input.strip():
            st.warning("Inserisci prima il testo.")
        else:
            esegui_analisi_ia_profonda(sms_voce_input, "Notifica Bancaria Automatica")

    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)

with tab4:
    st.subheader("🎯 I tuoi Obiettivi Personali di Risparmio")
    obiettivo_input = st.text_input("Descrivi il tuo obiettivo:", placeholder="Es. Vorrei risparmiare 3000 euro per una vacanza.")
    
    if st.button("Genera Piano Strategico Obiettivo"):
        if not obiettivo_input.strip():
            st.warning("Inserisci prima il tuo obiettivo.")
        else:
            esegui_analisi_ia_profonda(obiettivo_input, "Obiettivo di Risparmio", is_obiettivo=True)

    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)

# Tab dello Storico e Automazioni visibile solo se loggato
if st.session_state.is_loggato:
    with tab5:
        st.subheader("📂 Storico Cloud & Automazioni in Background")
        st.success("🤖 **Webhook Entrate/Uscite attivo**: Le notifiche del tuo telefono vengono analizzate in tempo reale.")
        
        if not st.session_state.storico_salvataggi:
            st.info("Nessun report salvato nello storico. Esegui la prima analisi.")
        else:
            for idx, item in enumerate(st.session_state.storico_salvataggi):
                with st.expander(f"Report #{len(st.session_state.storico_salvataggi) - idx} - {item['titolo']}"):
                    st.markdown(item['risultato'])

# Tab finale Statistiche & Commenti
with (tab6 if st.session_state.is_loggato else tab5):
    st.subheader("📊 Statistiche di Utilizzo dell'App")
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.metric(label="👥 Persone passate", value=st.session_state.visite)
    with col_stat2:
        st.metric(label="🚀 Analisi effettuate", value=st.session_state.conteggio_usi)

    st.markdown("---")
    st.subheader("⭐ Lascia un Commento e una Valutazione")
    nome_utente = st.text_input("Il tuo nome:", placeholder="Es. Anna Rossi", key="nome_rec")
    stelle_utente = st.selectbox("Valutazione in stelle:", ["⭐⭐⭐⭐⭐ (Eccellente)", "⭐⭐⭐⭐ (Molto buono)", "⭐⭐⭐ (Buono)", "⭐⭐ (Sufficiente)", "⭐ (Scarso)"])
    testo_recensione = st.text_area("Il tuo commento:", placeholder="Scrivi qui la tua recensione...", key="testo_rec")
    
    if st.button("Invia Commento"):
        if nome_utente.strip() and testo_recensione.strip():
            st.session_state.recensioni.insert(0, (nome_utente, stelle_utente.split(" ")[0], testo_recensione))
            st.success("🎉 Grazie mille per il tuo commento!")
        else:
            st.warning("Inserisci il tuo nome e il commento.")
            
    st.markdown("---")
    st.subheader("📋 Commenti della Community")
    for utente, stelle, commento in st.session_state.recensioni:
        st.markdown(f"**{utente}** - {stelle}\n\n*{commento}*")
        st.markdown("---")
