import streamlit as st
import google.generativeai as genai
import io
import pypdf
from PIL import Image
import pandas as pd
import plotly.express as px
import os
import json

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
            generation_config={"temperature": 0.8, "max_output_tokens": 2048}
        )
        gemini_disponibile = True
except Exception:
    gemini_disponibile = False

# --- FILE PERSISTENTI PER STATISTICHE E STORICO UTENTI ---
FILE_STATISTICHE = "contatore_visite.json"
FILE_STORICO_UTENTE = "storico_analisi.json"

def carica_json(file_path, default_val):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default_val

def salva_json(file_path, dati):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(dati, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

stats_correnti = carica_json(FILE_STATISTICHE, {"visite": 142, "utilizzi": 28})
storico_salvataggi_persistente = carica_json(FILE_STORICO_UTENTE, [])

if "sessione_registrata" not in st.session_state:
    st.session_state.sessione_registrata = True
    stats_correnti["visite"] += 1
    salva_json(FILE_STATISTICHE, stats_correnti)

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
st.write("Il tuo direttore finanziario personale, cinico ma saggio.")

# --- GESTIONE STATO UTENTE E LOGIN ---
if "is_loggato" not in st.session_state:
    st.session_state.is_loggato = False
if "utente_email" not in st.session_state:
    st.session_state.utente_email = ""
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
        st.sidebar.info("🔓 **Modalità Ospite attiva**.")
else:
    st.sidebar.success(f"Benvenuto, **{st.session_state.utente_email}**! 🔒")
    notifiche_push = st.sidebar.toggle("🔔 Notifiche Push", value=st.session_state.notifiche_attive)
    st.session_state.notifiche_attive = bool(notifiche_push)
        
    if st.sidebar.button("🚪 Esci (Logout)"):
        st.session_state.is_loggato = False
        st.session_state.utente_email = ""
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌍 Selezione Lingua & Valuta")
lista_lingue = [
    "Rilevamento Automatico (Auto)",
    "Italiano", "English", "Español", "Français", "Deutsch", 
    "Português", "Română", "العربية", "中文", "हिन्दी", 
    "日本語", "Русский", "Polski", "Nederlands", "Ελληνικά", 
    "Türkçe", "Українська", "Magyar", "Čeština", "Svenska", "한국어"
]
lingua_selezionata = st.sidebar.selectbox("Scegli la lingua:", lista_lingue)
valuta_selezionata = st.sidebar.selectbox("Valuta di riferimento:", ["Euro (€)", "Dollaro ($)", "Sterlina (£)", "Franco Svizzero (CHF)", "Yen (¥)"])

st.sidebar.markdown("---")
st.sidebar.markdown("### ⭐ Recensioni")
st.sidebar.markdown("⭐⭐⭐⭐⭐ **4.9 / 5.0**")

# Stato della sessione generale
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
        "📂 Storico Salvato",
        "⭐ Statistiche & Commenti"
    ])
else:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📥 Inserimento txt", 
        "📁 Importa File & Foto", 
        "🎤 Voce & SMS", 
        "🎯 Obiettivi", 
        "⭐ Statistiche & Commenti"
    ])

# Funzione centrale di analisi con struttura obbligatoria completa
def esegui_analisi_ia_profonda(contenuto_input, titolo_sorgente="Dati utente", is_image=False, image_obj=None, is_obiettivo=False):
    if not gemini_disponibile or not model:
        st.error("⚠ Configurazione API non rilevata o modello non disponibile.")
        return
    
    with st.spinner("💎 Il Direttore sta analizzando i conti..."):
        istruzione_lingua = ""
        if lingua_selezionata == "Rilevamento Automatico (Auto)":
            istruzione_lingua = "Rileva automaticamente la lingua e rispondi nella stessa."
        else:
            istruzione_lingua = f"Rispondi rigorosamente in lingua: {lingua_selezionata}."

        prompt = f"""
        {istruzione_lingua}
        Agisci come un direttore finanziario cinico, spietato ma saggio. Analizza i dati o l'obiettivo fornito: '{contenuto_input}' ({titolo_sorgente}).
        Usa rigorosamente la valuta '{valuta_selezionata}' per qualsiasi importo monetario.
        
        Rispondi seguendo rigorosamente ed esclusivamente questo schema in markdown, assicurandoti di includere ogni singola sezione richiesta:
        
        🛑 **Giudizio** [Un giudizio pesante, cinico e tagliente sulla situazione o sull'obiettivo]
        🔍 **Analisi** [Esame dettagliato delle voci, delle follie o delle pretese]
        💰 **Budget** [Riepilogo numerico chiaro, entrate, uscite, margine e stime in {valuta_selezionata}]
        💡 **Consiglio finanziario mirato** [Misure drastiche, pratiche e mirate per rimettere in riga i conti]
        
        💱 **Valuta di riferimento:** {valuta_selezionata}
        ⭐ **Stelle e Giudizio finale:** [Assegna da 1 a 5 stelle (es. ⭐⭐⭐☆☆) con una breve motivazione sarcastica]
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
                
                # Aggiorna statistiche
                stats = carica_json(FILE_STATISTICHE, {"visite": 142, "utilizzi": 28})
                stats["utilizzi"] += 1
                salva_json(FILE_STATISTICHE, stats)
                
                # Salva nello storico persistente su file locale
                nuovo_item = {
                    "titolo": titolo_sorgente,
                    "risultato": response.text
                }
                storico_attuale = carica_json(FILE_STORICO_UTENTE, [])
                storico_attuale.insert(0, nuovo_item)
                salva_json(FILE_STORICO_UTENTE, storico_attuale)
                
                st.success("Analisi completata!")
        except Exception as e:
            st.error(f"Errore durante l'analisi IA: {e}")

# Funzione grafico ultra-compatto
def mostra_grafico_compatto(id_grafico="default"):
    simbolo_val = valuta_selezionata.split("(")[-1].replace(")", "").strip()
    dati_grafico = pd.DataFrame({
        'Categoria': ['Casa', 'Cibo', 'Extra', 'Risparmio'],
        f'Importo ({simbolo_val})': [600, 350, 250, 150]
    })
    fig = px.pie(
        dati_grafico, 
        names='Categoria', 
        values=f'Importo ({simbolo_val})', 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(
        margin=dict(t=5, b=5, l=5, r=5),
        height=180,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True, key=f"grafico_pie_{id_grafico}")

# Sezione comune per Risultati, Grafico compatto, Azioni e Barra Dubbi
def renderizza_risultati_standard(id_tab):
    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        st.markdown("### 📊 Grafico")
        mostra_grafico_compatto(id_grafico=id_tab)
        
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)
        
        st.markdown("---")
        st.subheader("❓ Dubbi o domande")
        user_question = st.text_input("Chiedi un chiarimento al Direttore:", placeholder="Scrivi qui...", key=f"q_{id_tab}")
        
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            if st.button("Invia domanda", key=f"btn_domanda_{id_tab}"):
                if user_question.strip() and model:
                    with st.spinner("Elaborazione..."):
                        f_resp = model.generate_content(f"Rispondi in lingua {lingua_selezionata} usando la valuta {valuta_selezionata} e con tono cinico e tagliente basandoti sull'analisi: {user_question}")
                        if f_resp and f_resp.text:
                            st.markdown("### 💬 Risposta del Direttore:")
                            st.markdown(f_resp.text)
                            
        st.markdown("---")
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            st.download_button("📥 Scarica analisi", data=st.session_state.testo_risultato, file_name="report_finanziario.txt", key=f"download_{id_tab}")
        with col_act2:
            if st.button("🔄 Nuova analisi", key=f"btn_reset_{id_tab}"):
                st.session_state.analisi_fatta = False
                st.session_state.testo_risultato = ""
                st.rerun()

with tab1:
    st.subheader("📥 Inserimento Testuale Movimenti")
    user_text_input = st.text_area("Entrate e Uscite:", placeholder="Es. +2500 stipendio, -500 affitto...", label_visibility="collapsed", key="txt_input")
    
    if st.button("Analizza Movimenti", key="btn_tab1"):
        if not user_text_input.strip():
            st.warning("Inserisci prima i movimenti.")
        else:
            esegui_analisi_ia_profonda(user_text_input, "Inserimento Testuale")

    renderizza_risultati_standard("tab1")

with tab2:
    st.subheader("📁 Importa File & 📷 Foto")
    uploaded_file = st.file_uploader("Carica file o foto", type=["pdf", "txt", "csv", "jpg", "jpeg", "png"], key="file_uploader_tab2")
    
    if uploaded_file is not None:
        file_name_lower = uploaded_file.name.lower()
        is_img_file = file_name_lower.endswith(('.jpg', '.jpeg', '.png'))
        
        if is_img_file:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"Foto: {uploaded_file.name}", use_container_width=True)
        else:
            st.success(f"File caricato: **{uploaded_file.name}**")
        
        if st.button("🚀 Avvia Analisi File", key="btn_avvia_file"):
            try:
                bytes_data = uploaded_file.getvalue()
                if is_img_file:
                    image_obj = Image.open(io.BytesIO(bytes_data))
                    esegui_analisi_ia_profonda("", f"Foto: {uploaded_file.name}", is_image=True, image_obj=image_obj)
                elif file_name_lower.endswith('.pdf'):
                    pdf_file_obj = io.BytesIO(bytes_data)
                    reader = pypdf.PdfReader(pdf_file_obj)
                    extracted_pages = [page.extract_text() for page in reader.pages if page.extract_text()]
                    testo_estratto = "\n".join(extracted_pages) or "PDF privo di testo."
                    esegui_analisi_ia_profonda(testo_estratto[:30000], f"PDF: {uploaded_file.name}")
                else:
                    testo_estratto = bytes_data.decode("utf-8", errors="ignore")
                    esegui_analisi_ia_profonda(testo_estratto[:30000], f"Documento: {uploaded_file.name}")
            except Exception as e:
                st.error(f"Errore: {e}")

    renderizza_risultati_standard("tab2")

with tab3:
    st.subheader("🎤 Voce & SMS / Notifiche Bancarie")
    sms_voce_input = st.text_area("Testo notifica bancaria o trascrizione:", placeholder="Es. 'Pagamento POS -45€'...", key="sms_input")
    
    if st.button("Analizza Notifica", key="btn_tab3"):
        if not sms_voce_input.strip():
            st.warning("Inserisci il testo.")
        else:
            esegui_analisi_ia_profonda(sms_voce_input, "SMS / Notifica Bancaria")

    renderizza_risultati_standard("tab3")

with tab4:
    st.subheader("🎯 Obiettivi di Risparmio")
    obiettivo_input = st.text_input("Descrivi il tuo obiettivo:", placeholder="Es. Vorrei risparmiare 5000 euro.", key="obj_input")
    
    if st.button("Analizza Obiettivo", key="btn_tab4"):
        if not obiettivo_input.strip():
            st.warning("Inserisci l'obiettivo.")
        else:
            esegui_analisi_ia_profonda(obiettivo_input, "Obiettivo di Risparmio", is_obiettivo=True)

    renderizza_risultati_standard("tab4")

if st.session_state.is_loggato:
    with tab5:
        st.subheader("📂 Storico Salvato (Persistente)")
        st.info("Tutte le tue analisi precedenti rimangono salvate anche dopo la chiusura dell'app.")
        storico_salvataggi_persistente = carica_json(FILE_STORICO_UTENTE, [])
        if not storico_salvataggi_persistente:
            st.info("Nessun report salvato nello storico.")
        else:
            if st.button("🗑️ Svuota Storico Salvato", key="btn_pulisci_storico"):
                salva_json(FILE_STORICO_UTENTE, [])
                st.rerun()
                
            for idx, item in enumerate(storico_salvataggi_persistente):
                with st.expander(f"Analisi #{len(storico_salvataggi_persistente) - idx} - {item['titolo']}"):
                    st.markdown(item['risultato'])

with (tab6 if st.session_state.is_loggato else tab5):
    st.subheader("📊 Statistiche e Community")
    stats_file = carica_json(FILE_STATISTICHE, {"visite": 142, "utilizzi": 28})
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.metric(label="👥 Persone passate", value=stats_file["visite"])
    with col_stat2:
        st.metric(label="🚀 Analisi effettuate", value=stats_file["utilizzi"])

    st.markdown("---")
    st.subheader("⭐ Lascia un Commento")
    nome_utente = st.text_input("Il tuo nome:", placeholder="Es. Anna", key="nome_rec")
    stelle_utente = st.selectbox("Valutazione:", ["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐", "⭐"], key="sel_stelle")
    testo_recensione = st.text_area("Commento:", placeholder="La tua recensione...", key="testo_rec")
    
    if st.button("Invia Commento", key="btn_commento"):
        if nome_utente.strip() and testo_recensione.strip():
            st.session_state.recensioni.insert(0, (nome_utente, stelle_utente, testo_recensione))
            st.success("Grazie per il commento!")
        else:
            st.warning("Compila tutti i campi.")
            
    st.markdown("---")
    for utente, stelle, commento in st.session_state.recensioni:
        st.markdown(f"**{utente}** - {stelle}\n\n*{commento}*")
        st.markdown("---")
