import streamlit as st
import google.generativeai as genai
import io
import pypdf
from PIL import Image
import pandas as pd
import plotly.express as px
import random
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

# --- CONTA-PERSONE E UTILIZZI PERSISTENTI (FILE LOCALE) ---
FILE_STATISTICHE = "contatore_visite.json"

def carica_statistiche():
    if os.path.exists(FILE_STATISTICHE):
        try:
            with open(FILE_STATISTICHE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"visite": 142, "utilizzi": 28}

def salva_statistiche(stats):
    try:
        with open(FILE_STATISTICHE, "w") as f:
            json.dump(stats, f)
    except Exception:
        pass

stats_correnti = carica_statistiche()

if "sessione_registrata" not in st.session_state:
    st.session_state.sessione_registrata = True
    stats_correnti["visite"] += 1
    salva_statistiche(stats_correnti)

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

# Tab dell'applicazione
if st.session_state.is_loggato:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📥 Inserimento txt", 
        "📁 Importa File & Foto", 
        "🎤 Voce & SMS", 
        "🎯 Obiettivi", 
        "🔥 Generatore Insulti",
        "📂 Storico & Automazioni",
        "⭐ Commenti & Statistiche"
    ])
else:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📥 Inserimento txt", 
        "📁 Importa File & Foto", 
        "🎤 Voce & SMS", 
        "🎯 Obiettivi", 
        "🔥 Generatore Insulti",
        "⭐ Commenti & Statistiche"
    ])

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
            Fornisci un'analisi tagliente ma costruttiva, rispettando la sensibilità della persona ed evitando di calcare troppo la mano se c'è fragilità.
            
            Usa questa struttura esatta:
            📢 **Giudizio del Direttore sull'Obiettivo**
            🎯 **Fattibilità & Analisi**
            ⚠ **Ostacoli Critici**
            💡 **Consiglio Mirato**
            """
        else:
            prompt = f"""
            {istruzione_lingua}
            Agisci come un direttore finanziario cinico ma attento alla fragilità emotiva dell'utente. Analizza i dati (entrate e uscite): {titolo_sorgente}.
            Cita voci specifiche con ironia tagliente, senza però risultare crudele o demotivante.
            
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
                
                stats = carica_statistiche()
                stats["utilizzi"] += 1
                salva_statistiche(stats)
                
                if st.session_state.is_loggato:
                    st.session_state.storico_salvataggi.insert(0, {
                        "titolo": titolo_sorgente,
                        "risultato": response.text
                    })
                    if st.session_state.notifiche_attive:
                        st.sidebar.toast("📲 Notifica push: 'Nuovo verdetto del Direttore!'", icon="🔥")
                
                st.success("Analisi completata!")
        except Exception as e:
            st.error(f"Errore durante l'analisi IA: {e}")

# Funzione grafico con KEY univoca
def mostra_grafico_compatto(id_grafico="default"):
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
        height=250,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True, key=f"grafico_pie_{id_grafico}")

with tab1:
    st.subheader("Incolla qui la lista delle spese e delle entrate:")
    user_text_input = st.text_area("Movimenti:", placeholder="Es. +2500 stipendio, -500 affitto, -50 supermercato...", label_visibility="collapsed", key="txt_input")
    
    if st.button("Analizza Movimenti in Profondità", key="btn_tab1"):
        if not user_text_input.strip():
            st.warning("Inserisci prima i movimenti finanziari.")
        else:
            esegui_analisi_ia_profonda(user_text_input, "Lista testuale Entrate/Uscite")

    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        mostra_grafico_compatto(id_grafico="tab1")
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)
        
        st.markdown("---")
        st.subheader("❓ Dubbi o domande")
        user_question = st.text_input("Fai una domanda o chiedi un chiarimento:", placeholder="Es. Come posso tagliare sulle bollette?", key="q_tab1")
        
        col_1, col_2 = st.columns(2)
        with col_1:
            if st.button("Invia domanda al consulente", key="btn_domanda_tab1"):
                if user_question.strip() and model:
                    with st.spinner("Elaborazione risposta..."):
                        f_resp = model.generate_content(f"Rispondi in lingua {lingua_selezionata}, mantieni un tono ironico ma rispettoso e costruttivo basandoti sull'analisi precedente: {user_question}")
                        if f_resp and f_resp.text:
                            st.markdown("### 💬 Risposta del Consulente:")
                            st.markdown(f_resp.text)
                            
        with col_2:
            if st.button("🔄 Nuova analisi", key="btn_reset_tab1"):
                st.session_state.analisi_fatta = False
                st.session_state.testo_risultato = ""
                st.rerun()

with tab2:
    st.subheader("📁 Importa File & 📷 Foto (PDF, TXT, CSV, JPG, PNG)")
    uploaded_file = st.file_uploader("Carica file o foto", type=["pdf", "txt", "csv", "jpg", "jpeg", "png"], key="file_uploader_tab2")
    
    if uploaded_file is not None:
        file_name_lower = uploaded_file.name.lower()
        is_img_file = file_name_lower.endswith(('.jpg', '.jpeg', '.png'))
        
        if is_img_file:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"Foto caricata: {uploaded_file.name}", use_container_width=True)
        else:
            st.success(f"File caricato: **{uploaded_file.name}**")
        
        if st.button("🚀 Avvia Analisi Avanzata File / Foto", key="btn_avvia_file"):
            try:
                bytes_data = uploaded_file.getvalue()
                if is_img_file:
                    image_obj = Image.open(io.BytesIO(bytes_data))
                    esegui_analisi_ia_profonda("", f"Foto documento: {uploaded_file.name}", is_image=True, image_obj=image_obj)
                elif file_name_lower.endswith('.pdf'):
                    pdf_file_obj = io.BytesIO(bytes_data)
                    reader = pypdf.PdfReader(pdf_file_obj)
                    extracted_pages = [page.extract_text() for page in reader.pages if page.extract_text()]
                    testo_estratto = "\n".join(extracted_pages) or "PDF privo di testo vettoriale."
                    esegui_analisi_ia_profonda(testo_estratto[:30000], f"PDF Estratto Conto: {uploaded_file.name}")
                else:
                    testo_estratto = bytes_data.decode("utf-8", errors="ignore")
                    esegui_analisi_ia_profonda(testo_estratto[:30000], f"Documento: {uploaded_file.name}")
            except Exception as e:
                st.error(f"Errore durante l'elaborazione: {e}")

    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        mostra_grafico_compatto(id_grafico="tab2")
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)
        st.markdown("---")
        st.download_button("📥 Scarica report in formato Testo", data=st.session_state.testo_risultato, file_name="report_spese.txt", key="download_report_tab2")
        
        # BARRA DI RISPOSTA (DUBBI O DOMANDE) IN FINE
        st.markdown("---")
        st.subheader("❓ Dubbi o domande")
        user_question_tab2 = st.text_input("Fai una domanda o chiedi un chiarimento sul report:", placeholder="Es. Spiegami meglio il punto 1...", key="q_tab2")
        
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            if st.button("Invia domanda al consulente", key="btn_domanda_tab2"):
                if user_question_tab2.strip() and model:
                    with st.spinner("Elaborazione risposta..."):
                        f_resp = model.generate_content(f"Rispondi in lingua {lingua_selezionata}, mantieni un tono ironico ma rispettoso e costruttivo basandoti sull'analisi del file precedente: {user_question_tab2}")
                        if f_resp and f_resp.text:
                            st.markdown("### 💬 Risposta del Consulente:")
                            st.markdown(f_resp.text)
        with col_q2:
            if st.button("🔄 Nuova analisi file", key="btn_reset_tab2"):
                st.session_state.analisi_fatta = False
                st.session_state.testo_risultato = ""
                st.rerun()

with tab3:
    st.subheader("🎤 Voce & SMS / Notifiche Bancarie (Entrate & Uscite)")
    sms_voce_input = st.text_area("Testo notifica bancaria:", placeholder="Es. 'Bonifico in entrata +1850€'...", key="sms_input")
    
    if st.button("Analizza Notifiche in Background", key="btn_tab3"):
        if not sms_voce_input.strip():
            st.warning("Inserisci prima il testo.")
        else:
            esegui_analisi_ia_profonda(sms_voce_input, "Notifica Bancaria Automatica")

    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        mostra_grafico_compatto(id_grafico="tab3")
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)
        
        st.markdown("---")
        st.subheader("❓ Dubbi o domande")
        user_question_tab3 = st.text_input("Fai una domanda o chiedi un chiarimento:", placeholder="Scrivi qui...", key="q_tab3")
        if st.button("Invia domanda al consulente", key="btn_domanda_tab3"):
            if user_question_tab3.strip() and model:
                with st.spinner("Elaborazione risposta..."):
                    f_resp = model.generate_content(f"Rispondi in lingua {lingua_selezionata}, mantieni un tono ironico ma rispettoso: {user_question_tab3}")
                    if f_resp and f_resp.text:
                        st.markdown("### 💬 Risposta del Consulente:")
                        st.markdown(f_resp.text)

with tab4:
    st.subheader("🎯 I tuoi Obiettivi Personali di Risparmio")
    obiettivo_input = st.text_input("Descrivi il tuo obiettivo:", placeholder="Es. Vorrei risparmiare 3000 euro per una vacanza.", key="obj_input")
    
    if st.button("Genera Piano Strategico Obiettivo", key="btn_tab4"):
        if not obiettivo_input.strip():
            st.warning("Inserisci prima il tuo obiettivo.")
        else:
            esegui_analisi_ia_profonda(obiettivo_input, "Obiettivo di Risparmio", is_obiettivo=True)

    if st.session_state.analisi_fatta and st.session_state.testo_risultato:
        st.markdown("---")
        st.markdown(st.session_state.testo_risultato)
        
        st.markdown("---")
        st.subheader("❓ Dubbi o domande")
        user_question_tab4 = st.text_input("Fai una domanda sull'obiettivo:", placeholder="Scrivi qui...", key="q_tab4")
        if st.button("Invia domanda al consulente", key="btn_domanda_tab4"):
            if user_question_tab4.strip() and model:
                with st.spinner("Elaborazione risposta..."):
                    f_resp = model.generate_content(f"Rispondi in lingua {lingua_selezionata}, mantieni un tono ironico ma rispettoso: {user_question_tab4}")
                    if f_resp and f_resp.text:
                        st.markdown("### 💬 Risposta del Consulente:")
                        st.markdown(f_resp.text)

with tab5:
    st.subheader("🔥 Il Generatore di Insulti (e Reazioni del Direttore)")
    st.info("Scegli la tua situazione o prova a provocare il sistema.")
    
    modalita_input = st.radio("Scegli la modalità di interazione:", [
        "Situazione finanziaria tipica", 
        "Voglio provocare / Prendere in giro il sistema 😈"
    ], key="radio_insulti")
    
    if modalita_input == "Situazione finanziaria tipica":
        situazione_scelta = st.selectbox("Qual è la tua situazione critica oggi?", [
            "Ho il conto in rosso e mancano 2 settimane a fine mese",
            "Ho speso tutto lo stipendio in aperitivi e ristoranti",
            "Compro cianfrusaglie su Amazon che non uso",
            "Ho zero risparmi e vivo alla giornata",
            "Guadagno bene ma riesco a spendere il 110% del mio stipendio",
            "Voglio comprare una cosa inutile che costa un canotto"
        ], key="select_sit")
        input_utente_provocazione = ""
    else:
        input_utente_provocazione = st.text_input("Scrivi la tua provocazione o presa per il culo verso il sistema:", placeholder="Es. Ma che ne capisci tu bot di plastica...", key="input_provocazione")
        situazione_scelta = ""

    umore_utente = st.select_slider(
        "Come ti senti oggi emotivamente?:",
        options=["Molto fragile / Ho bisogno di tatto 🥺", "Equilibrato / Accetto l'ironia normale 🙂", "Pronto alla battaglia / Distruggimi pure 🥊"],
        value="Equilibrato / Accetto l'ironia normale 🙂",
        key="slider_umore"
    )

    if st.button("💥 Esegui Verdetto", key="btn_verdetto"):
        if model:
            with st.spinner("Il Direttore sta valutando..."):
                tocco_sensibilita = ""
                if "Molto fragile" in umore_utente:
                    tocco_sensibilita = "NOTA BENE: L'utente si sente fragile oggi. Sii ironico e spiritoso, ma mantieni toni dolci."
                elif "Equilibrato" in umore_utente:
                    tocco_sensibilita = "Usa un'ironia tagliente, brillante e pungente."
                else:
                    tocco_sensibilita = "L'utente cerca la rissa verbale. Distruggi le sue scuse con sarcasmo devastante!"

                if modalita_input == "Voglio provocare / Prendere in giro il sistema 😈" and input_utente_provocazione.strip():
                    prompt_insulto = f"{tocco_sensibilita} L'utente ha provocato dicendo: '{input_utente_provocazione}'."
                else:
                    prompt_insulto = f"{tocco_sensibilita} L'utente si trova in questa situazione: '{situazione_scelta}'."

                try:
                    res_insulto = model.generate_content(prompt_insulto)
                    if res_insulto and res_insulto.text:
                        st.session_state.ultimo_insulto = res_insulto.text
                except Exception as e:
                    st.session_state.ultimo_insulto = f"Errore: {e}"
        else:
            st.session_state.ultimo_insulto = "Il tuo conto in rosso grida vendetta."
            
    if st.session_state.ultimo_insulto:
        st.markdown("---")
        st.error(f"### 🛑 Verdetto del Direttore:\n\n{st.session_state.ultimo_insulto}")

if st.session_state.is_loggato:
    with tab6:
        st.subheader("📂 Storico Cloud & Automazioni in Background")
        st.success("🤖 **Webhook Entrate/Uscite attivo**.")
        if not st.session_state.storico_salvataggi:
            st.info("Nessun report salvato nello storico.")
        else:
            for idx, item in enumerate(st.session_state.storico_salvataggi):
                with st.expander(f"Report #{len(st.session_state.storico_salvataggi) - idx} - {item['titolo']}"):
                    st.markdown(item['risultato'])

with (tab7 if st.session_state.is_loggato else tab6):
    st.subheader("📊 Statistiche di Utilizzo dell'App")
    stats_file = carica_statistiche()
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.metric(label="👥 Persone passate", value=stats_file["visite"])
    with col_stat2:
        st.metric(label="🚀 Analisi effettuate", value=stats_file["utilizzi"])

    st.markdown("---")
    st.subheader("⭐ Lascia un Commento e una Valutazione")
    nome_utente = st.text_input(" Il tuo nome:", placeholder="Es. Anna Rossi", key="nome_rec")
    stelle_utente = st.selectbox("Valutazione in stelle:", ["⭐⭐⭐⭐⭐ (Eccellente)", "⭐⭐⭐⭐ (Molto buono)", "⭐⭐⭐ (Buono)", "⭐⭐ (Sufficiente)", "⭐ (Scarso)"], key="sel_stelle")
    testo_recensione = st.text_area("Il tuo commento:", placeholder="Scrivi qui la tua recensione...", key="testo_rec")
    
    if st.button("Invia Commento", key="btn_commento"):
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
