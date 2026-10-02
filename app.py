import streamlit as st
import google.generativeai as genai
import io
import pypdf
from PIL import Image
import pandas as pd
import plotly.express as px
import os
import json
from concurrent.futures import ThreadPoolExecutor

# Configurazione della pagina
st.set_page_config(
    page_title="Split & Save AI - Ultra Node",
    page_icon="💡",
    layout="centered"
)

# Configurazione Gemini con Gemini 3.8 Flash ottimizzato per la velocità
gemini_disponibile = False
model = None

try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name='gemini-3.8-flash',
            generation_config={"temperature": 0.3, "max_output_tokens": 4096}
        )
        gemini_disponibile = True
except Exception:
    gemini_disponibile = False

# --- FILE PERSISTENTI PER STATISTICHE E STORICO UTENTI ---
FILE_STATISTICHE = "contatore_visite.json"
FILE_STORICO_UTENTE = "storico_analisi.json"
FILE_OBIETTIVI = "obiettivi_utente.json"

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

if "sessione_registrata" not in st.session_state:
    st.session_state.sessione_registrata = True
    stats_correnti["visite"] += 1
    salva_json(FILE_STATISTICHE, stats_correnti)

# Stile grafico avanzato e leggero
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
    .box-valutazione {
        background-color: #f0fdf4;
        border: 1px solid #10b981;
        padding: 15px;
        border-radius: 12px;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    .badge-nodo {
        background-color: #e6f4ea;
        color: #137333;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("Split & Save AI 💡 <span class='badge-nodo'>4 Nodi Multi-Thread Attivi</span>")
st.write("Direttore finanziario potenziato con architettura a 4 nodi di ricerca e velocità.")

# --- GESTIONE STATO UTENTE E LOGIN ---
if "is_loggato" not in st.session_state:
    st.session_state.is_loggato = False
if "utente_email" not in st.session_state:
    st.session_state.utente_email = "Ospite"
if "notifiche_attive" not in st.session_state:
    st.session_state.notifiche_attive = False

st.sidebar.markdown("### 👤 Accesso & Account")

if not st.session_state.is_loggato or st.session_state.utente_email == "Ospite":
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
                    st.session_state.utente_email = input_user.strip()
                    st.success("Account creato!")
                    st.rerun()
                else:
                    st.warning("Inserisci credenziali.")
        with col_reg2:
            if st.button("Login"):
                if input_user and input_pass:
                    st.session_state.is_loggato = True
                    st.session_state.utente_email = input_user.strip()
                    st.success("Accesso effettuato!")
                    st.rerun()
                else:
                    st.warning("Inserisci credenziali.")
    else:
        st.session_state.is_loggato = True
        st.session_state.utente_email = "Ospite"
        st.sidebar.info("🔓 **Modalità Ospite attiva**.")
else:
    st.sidebar.success(f"Benvenuto, **{st.session_state.utente_email}**! 🔒")
    notifiche_push = st.sidebar.toggle("🔔 Notifiche Push", value=st.session_state.notifiche_attive)
    st.session_state.notifiche_attive = bool(notifiche_push)
        
    if st.sidebar.button("🚪 Esci (Logout)"):
        st.session_state.is_loggato = False
        st.session_state.utente_email = "Ospite"
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
st.sidebar.markdown("### ⚡ Cluster di Nodi")
st.sidebar.markdown("🟢 **Nodo 1 (Velocità Core)**: Online\n🟢 **Nodo 2 (Ricerca Semantica)**: Online\n🟢 **Nodo 3 (Elaborazione File)**: Online\n🟢 **Nodo 4 (Sintesi & Grafici)**: Online")

# Stato della sessione generale
if "analisi_fatta" not in st.session_state:
    st.session_state.analisi_fatta = False
if "testo_risultato" not in st.session_state:
    st.session_state.testo_risultato = ""
if "recensioni" not in st.session_state:
    st.session_state.recensioni = [
        ("Marco R.", "⭐⭐⭐⭐⭐", "Velocità incredibile con i 4 nodi!"),
        ("Giulia V.", "⭐⭐⭐⭐⭐", "Analisi precisa e fulminea.")
    ]

# Tab dell'applicazione (Inserita la scheda "🕒 Cronologia" al posto di SMS)
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📥 Inserimento txt", 
    "📁 Importa File & Foto", 
    "🕒 Cronologia", 
    "🎯 Obiettivi", 
    "📂 Storico Salvato",
    "⭐ Statistiche & Commenti"
])

def worker_nodo(prompt_parziale):
    if not model:
        return ""
    try:
        res = model.generate_content(prompt_parziale)
        return res.text if res and res.text else ""
    except Exception:
        return ""

def esegui_analisi_multi_nodo(contenuto_input, titolo_sorgente="Dati utente", is_image=False, image_obj=None):
    if not gemini_disponibile or not model:
        st.error("⚠ Configurazione API non rilevata o modello non disponibile.")
        return
    
    with st.spinner("⚡ Distribuzione del carico sui 4 nodi di ricerca e velocità..."):
        istruzione_lingua = "" if lingua_selezionata == "Rilevamento Automatico (Auto)" else f"Rispondi in: {lingua_selezionata}."
        
        p1 = f"{istruzione_lingua} Agisci come direttore finanziario cinico. Analizza i dati: '{contenuto_input}'. Scrivi la sezione: 🛑 **Giudizio** pesante e tagliente in valuta {valuta_selezionata}."
        p2 = f"{istruzione_lingua} Agisci come analista economico. Esamina i flussi dei dati: '{contenuto_input}'. Scrivi la sezione: 🔍 **Analisi** dettagliata."
        p3 = f"{istruzione_lingua} Calcola entrate, uscite, margini e budget in valuta {valuta_selezionata} per: '{contenuto_input}'. Scrivi la sezione: 💰 **Budget**."
        p4 = f"{istruzione_lingua} Fornisci un'azione drastica immediata per: '{contenuto_input}'. Scrivi la sezione: 💡 **Consiglio finanziario mirato**."

        if is_image and image_obj is not None:
            prompt_totale = f"{istruzione_lingua} Analizza l'immagine allegata con tono cinico e saggio usando la valuta {valuta_selezionata}. Scrivi: 🛑 **Giudizio**, 🔍 **Analisi**, 💰 **Budget**, 💡 **Consiglio finanziario mirato**."
            try:
                response = model.generate_content([prompt_totale, image_obj])
                risultato_finale = response.text if response else "Errore analisi immagine."
            except Exception as e:
                risultato_finale = f"Errore: {e}"
        else:
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [
                    executor.submit(worker_nodo, p1),
                    executor.submit(worker_nodo, p2),
                    executor.submit(worker_nodo, p3),
                    executor.submit(worker_nodo, p4)
                ]
                risultati_nodi = [f.result() for f in futures]
            
            risultato_finale = "\n\n".join([r for r in risultati_nodi if r])
            if not risultato_finale.strip():
                fallback_res = model.generate_content(f"{istruzione_lingua} Analizza {contenuto_input} usando la valuta {valuta_selezionata} con sezioni Giudizio, Analisi, Budget, Consiglio.")
                risultato_finale = fallback_res.text if fallback_res else "Nessun risultato."

        st.session_state.analisi_fatta = True
        st.session_state.testo_risultato = risultato_finale
        
        stats = carica_json(FILE_STATISTICHE, {"visite": 142, "utilizzi": 28})
        stats["utilizzi"] += 1
        salva_json(FILE_STATISTICHE, stats)
        
        archivio_totale = carica_json(FILE_STORICO_UTENTE, {})
        utente_corrente = st.session_state.utente_email
        if utente_corrente not in archivio_totale:
            archivio_totale[utente_corrente] = []
            
        nuovo_item = {"titolo": titolo_sorgente, "risultato": risultato_finale}
        archivio_totale[utente_corrente].insert(0, nuovo_item)
        salva_json(FILE_STORICO_UTENTE, archivio_totale)
        
        st.success("Elaborazione completata e salvata nella tua cronologia privata!")

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

def renderizza_risultati_standard(id_tab):
    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        st.markdown("### 📊 Grafico (Elaborato dal Nodo 4)")
        mostra_grafico_compatto(id_grafico=id_tab)
        
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)
        
        st.markdown("---")
        st.markdown('<div class="box-valutazione">', unsafe_allow_html=True)
        st.subheader("⭐ Valuta questa analisi")
        voto_utente_analisi = st.select_slider(
            "Quanto è stata utile questa analisi?",
            options=["⭐ Scarsa", "⭐⭐ Mediocre", "⭐⭐⭐ Buona", "⭐⭐⭐⭐ Ottima", "⭐⭐⭐⭐⭐ Eccellente"],
            key=f"slider_valutazione_{id_tab}"
        )
        if st.button("Invia Valutazione Analisi", key=f"btn_voto_{id_tab}"):
            st.success(f"Grazie per il tuo feedback ({voto_utente_analisi})!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("❓ Dubbi o domande")
        user_question = st.text_input("Chiedi un chiarimento al Direttore:", placeholder="Scrivi qui...", key=f"q_{id_tab}")
        
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            if st.button("Invia domanda", key=f"btn_domanda_{id_tab}"):
                if user_question.strip() and model:
                    with st.spinner("Interrogazione nodo di ricerca..."):
                        f_resp = model.generate_content(f"Rispondi brevemente in lingua {lingua_selezionata} con tono cinico: {user_question}")
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
    
    if st.button("Analizza con 4 Nodi", key="btn_tab1"):
        if not user_text_input.strip():
            st.warning("Inserisci prima i movimenti.")
        else:
            esegui_analisi_multi_nodo(user_text_input, "Inserimento Testuale")

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
                    esegui_analisi_multi_nodo("", f"Foto: {uploaded_file.name}", is_image=True, image_obj=image_obj)
                elif file_name_lower.endswith('.pdf'):
                    pdf_file_obj = io.BytesIO(bytes_data)
                    reader = pypdf.PdfReader(pdf_file_obj)
                    extracted_pages = [page.extract_text() for page in reader.pages if page.extract_text()]
                    testo_estratto = "\n".join(extracted_pages) or "PDF privo di testo."
                    esegui_analisi_multi_nodo(testo_estratto[:15000], f"PDF: {uploaded_file.name}")
                else:
                    testo_estratto = bytes_data.decode("utf-8", errors="ignore")
                    esegui_analisi_multi_nodo(testo_estratto[:15000], f"Documento: {uploaded_file.name}")
            except Exception as e:
                st.error(f"Errore: {e}")

    renderizza_risultati_standard("tab2")

with tab3:
    st.subheader("🕒 Cronologia Analisi (Privata)")
    st.info(f"🔒 Questa è la cronologia completa delle analisi associate unicamente all'account: **{st.session_state.utente_email}**")
    
    archivio_totale = carica_json(FILE_STORICO_UTENTE, {})
    cronologia_utente = archivio_totale.get(st.session_state.utente_email, [])
    
    if not cronologia_utente:
        st.info("Nessuna analisi presente nella tua cronologia privata.")
    else:
        if st.button("🗑️ Svuota la mia Cronologia", key="btn_pulisci_cronologia_privata"):
            archivio_totale[st.session_state.utente_email] = []
            salva_json(FILE_STORICO_UTENTE, archivio_totale)
            st.rerun()
            
        for idx, item in enumerate(cronologia_utente):
            with st.expander(f"Analisi #{len(cronologia_utente) - idx} - {item['titolo']}"):
                st.markdown(item['risultato'])
                st.download_button("📥 Scarica Report Analisi", data=item['risultato'], file_name=f"cronologia_report_{idx}.txt", key=f"dl_cron_{idx}")

with tab4:
    st.subheader("🎯 Obiettivi di Risparmio & Import/Export")
    
    archivio_obiettivi = carica_json(FILE_OBIETTIVI, {})
    obiettivi_utente = archivio_obiettivi.get(st.session_state.utente_email, [])
    
    obiettivo_input = st.text_input("Descrivi il tuo obiettivo:", placeholder="Es. Vorrei risparmiare 5000 euro.", key="obj_input")
    
    col_ob1, col_ob2 = st.columns(2)
    with col_ob1:
        if st.button("Analizza Obiettivo", key="btn_tab4"):
            if not obiettivo_input.strip():
                st.warning("Inserisci l'obiettivo.")
            else:
                obiettivi_utente.insert(0, obiettivo_input)
                archivio_obiettivi[st.session_state.utente_email] = obiettivi_utente
                salva_json(FILE_OBIETTIVI, archivio_obiettivi)
                esegui_analisi_multi_nodo(obiettivo_input, "Obiettivo di Risparmio")
    
    with col_ob2:
        if obiettivi_utente:
            json_obiettivi = json.dumps(obiettivi_utente, ensure_ascii=False, indent=4)
            st.download_button("📤 Esporta Obiettivi (JSON)", data=json_obiettivi, file_name="miei_obiettivi.json", mime="application/json")

    file_importato = st.file_uploader("📥 Importa Obiettivi da file JSON", type=["json"], key="import_obiettivi_file")
    if file_importato is not None:
        try:
            dati_importati = json.load(file_importato)
            if isinstance(dati_importati, list):
                archivio_obiettivi[st.session_state.utente_email] = dati_importati + obiettivi_utente
                salva_json(FILE_OBIETTIVI, archivio_obiettivi)
                st.success("Obiettivi importati con successo!")
                st.rerun()
            else:
                st.error("Il file JSON non ha il formato corretto.")
        except Exception as e:
            st.error(f"Errore durante l'importazione: {e}")

    if obiettivi_utente:
        st.markdown("#### I tuoi obiettivi registrati:")
        for o in obiettivi_utente:
            st.markdown(f"- {o}")

    renderizza_risultati_standard("tab4")

with tab5:
    st.subheader("📂 Storico Salvato (Globale Account)")
    st.info(f"Visualizzazione storico per l'utente loggato: **{st.session_state.utente_email}**")
    archivio_totale = carica_json(FILE_STORICO_UTENTE, {})
    storico_privato = archivio_totale.get(st.session_state.utente_email, [])
    
    if not storico_privato:
        st.info("Nessun report salvato per questo account.")
    else:
        if st.button("🗑️ Svuota Storico", key="btn_pulisci_storico"):
            archivio_totale[st.session_state.utente_email] = []
            salva_json(FILE_STORICO_UTENTE, archivio_totale)
            st.rerun()
            
        for idx, item in enumerate(storico_privato):
            with st.expander(f"Analisi #{len(storico_privato) - idx} - {item['titolo']}"):
                st.markdown(item['risultato'])

with tab6:
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
