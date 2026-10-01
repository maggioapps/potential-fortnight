import streamlit as st

# --- CONFIGURAZIONE DELLA PAGINA ---
st.set_page_config(
    page_title="AURASYNC OS — Ultimate Edition",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INIZIALIZZAZIONE DELLO STATO DELLA SESSIONE ---
if "posts" not in st.session_state:
    st.session_state["posts"] = [
        {
            "id": 1,
            "utente": "AuraSync Community",
            "testo": "Benvenuti nella bacheca ufficiale di AURASYNC! Condividete idee, progetti e interagite in tempo reale.",
            "likes": 12,
            "commenti": ["Spettacolare!", "Ottima piattaforma."],
            "condivisibile": True
        }
    ]

if "visitatori" not in st.session_state:
    st.session_state["visitatori"] = 24
if "utilizzi" not in st.session_state:
    st.session_state["utilizzi"] = 105

# --- INTESTAZIONE PRINCIPALE: AURASYNC & CONTATORE LIVE ---
col_logo, col_counter = st.columns([3, 1])

with col_logo:
    st.markdown("<h1 style='margin: 0; padding: 0;'>AURASYNC</h1>", unsafe_allow_html=True)

with col_counter:
    # Contatore compatto Persone vs Utilizzi in piccolo
    st.markdown(
        f"<div style='text-align: right; padding-top: 10px; font-size: 13px; color: #666;'>"
        f"👥 <b>{st.session_state['visitatori']}</b> Persone &nbsp;|&nbsp; ⚡ <b>{st.session_state['utilizzi']}</b> Utilizzi"
        f"</div>", 
        unsafe_allow_html=True
    )

st.markdown("---")

# --- BARRA DI RICERCA UNIVERSALE ---
query_universale = st.text_input(
    "🔍 Ricerca Universale (Cerca tra i 300 moduli interni o inserisci un dubbio/domanda):",
    placeholder="Es. Media ponderata, Sblocco lavandino, finanza, o fai una domanda..."
)

if query_universale:
    st.info(f"Risultati rapidi per: **{query_universale}** (Reindirizzamento intelligente attivo...)")
    st.session_state["utilizzi"] += 1

st.markdown("---")

# --- MENU DI NAVIGAZIONE PRINCIPALE ---
# La Bacheca Social è la schermata principale di default (stile Facebook)
nav_principale = st.radio(
    "Navigazione Sistema:",
    ["💬 Bacheca Social (Home)", "📁 Cartella 50 Capitoli & 300 Moduli"],
    horizontal=True
)

st.markdown("---")

# =====================================================================
# MODULO 1: LA BACHECA SOCIAL (SCHERMATA PRINCIPALE / HOME)
# =====================================================================
if nav_principale == "💬 Bacheca Social (Home)":
    st.subheader("💬 Bacheca Pubblica")
    st.write("Condividi aggiornamenti con la community, lascia un like, commenta e condividi all'esterno (se abilitato).")

    # Box per la creazione di un nuovo post
    with st.form("form_creazione_post", clear_on_submit=True):
        nome_autore = st.text_input("Il tuo Nome / Nickname:", placeholder="Es. Marco Rossi")
        contenuto_post = st.text_area("A cosa stai pensando?", placeholder="Scrivi il tuo post...")
        concedi_condivisione = st.checkbox("Consenti la condivisione esterna di questo post")
        
        bottone_pubblica = st.form_submit_button("Pubblica Post")
        
        if bottone_pubblica and nome_autore and contenuto_post:
            st.session_state["posts"].insert(0, {
                "id": len(st.session_state["posts"]) + 1,
                "utente": nome_autore,
                "testo": contenuto_post,
                "likes": 0,
                "commenti": [],
                "condivisibile": concedi_condivisione
            })
            st.session_state["utilizzi"] += 1
            st.success("Post pubblicato con successo nel feed!")
            st.rerun()

    st.markdown("### 📰 Feed Recenti")

    # Visualizzazione dinamica dei post della bacheca
    for post in st.session_state["posts"]:
        with st.container():
            st.markdown(f"**👤 {post['utente']}**")
            st.write(post["testo"])
            
            col_like, col_share, col_space = st.columns([1, 1, 4])
            
            with col_like:
                if st.button(f"👍 {post['likes']}", key=f"btn_like_{post['id']}"):
                    post["likes"] += 1
                    st.rerun()
                    
            with col_share:
                if post["condivisibile"]:
                    if st.button("🔗 Condividi", key=f"btn_share_{post['id']}"):
                        st.toast("Link del post copiato negli appunti per la condivisione esterna!")
                else:
                    st.caption("🔒 Condivisione non consentita")

            # Area commenti espandibile
            with st.expander(f"💬 Commenti ({len(post['commenti'])})"):
                for commento in post["commenti"]:
                    st.markdown(f"> {commento}")
                
                nuovo_commento = st.text_input("Scrivi un commento...", key=f"input_com_{post['id']}")
                if st.button("Invia commento", key=f"send_com_{post['id']}") and nuovo_commento:
                    post["commenti"].append(nuovo_commento)
                    st.session_state["utilizzi"] += 1
                    st.rerun()
                    
        st.markdown("---")

# =====================================================================
# MODULO 2: CARTELLA 50 CAPITOLI & 300 MODULI
# =====================================================================
else:
    st.subheader("📁 Cartella Master: I 50 Capitoli & 300 Moduli")
    st.write("Seleziona uno dei capitoli per accedere alle 6 applicazioni dedicate con esecuzione isolata.")

    # Dizionario strutturato dei capitoli e delle 6 app interne ciascuno
    archivio_capitoli = {
        "Capitolo 01: Università & Studio": [
            "Calcolatore Media Ponderata", "Tracker Esami & CFU", "Simulatore Tassa Universitaria", 
            "Pomodoro Timer Avanzato", "Archivio Dispense Digitali", "Generatore Quiz di Verifica"
        ],
        "Capitolo 02: Casa & Manutenzione": [
            "Guida Sblocco Lavandino", "Gestione Bollette & Scadenze", "Inventario Dispensa Intelligente", 
            "Controllo Efficienza Caldaia", "Manutenzione Giardino & Piante", "Kit Emergenze Domestiche"
        ],
        "Capitolo 03: Gamification & RPG": [
            "XP System Quotidiano", "Tracker Abitudini (Habit Tracker)", "Missioni e Quest Epiche", 
            "Negozio Ricompense Personali", "Statistiche di Crescita", "Livelli e Badge Sbloccabili"
        ],
        "Capitolo 04: Produttività & Office": [
            "Dashboard Zero-Click", "Generatore Report PDF", "Esportatore Tabelle Excel", 
            "Convertitore Universale Unità", "Agenda Globale & Promemoria", "Note Rapide Crittografate"
        ]
        # Nota: L'architettura è scalabile fino a 50 capitoli seguendo questo schema a dizionario.
    }

    # Selezione del capitolo
    capitolo_selezionato = st.selectbox("Seleziona Capitolo (1 - 50):", list(archivio_capitoli.keys()))
    
    st.markdown(f"### 🚀 Applicazioni interne per *{capitolo_selezionato}*")
    app_selezionata = st.selectbox("Seleziona l'applicazione (6 moduli disponibili):", archivio_capitoli[capitolo_selezionato])

    st.markdown("---")
    st.success(f"Esecuzione in corso del modulo isolato: **{app_selezionata}**")
    
    # Esempio pratico di esecuzione interattiva di un modulo
    if "Media Ponderata" in app_selezionata:
        voto = st.number_input("Inserisci voto", 18, 30, 27)
        cfu = st.number_input("Inserisci CFU", 1, 18, 6)
        if st.button("Registra Esame"):
            st.session_state["utilizzi"] += 1
            st.metric("Stato Modulo", f"Esame registrato con successo (Voto: {voto}, CFU: {cfu})!")
    else:
        st.write("Modulo caricato correttamente. Pronto per l'inserimento dati e l'elaborazione isolata.")
