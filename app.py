import streamlit as st

# Configurazione di sistema multi-motore
st.set_page_config(
    page_title="AURASYNC Enterprise OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inizializzazione sicura dello state globale (senza loop)
if "initialized" not in st.session_state:
    st.session_state["initialized"] = True
    st.session_state["posts"] = [
        {
            "id": 1,
            "utente": "AuraSync Core",
            "testo": "Sistema operativo mobile-first inizializzato con successo. Tutti i motori sono online.",
            "likes": 42,
            "commenti": ["Motore 1 attivo", "Connessione stabile"]
        }
    ]
    st.session_state["visitatori"] = 1240
    st.session_state["utilizzi"] = 3890

# Layout principale: Header stile OS
col_title, col_stats = st.columns([2, 2])

with col_title:
    st.markdown("<h2 style='margin:0; color:#FF4B4B;'>⚡ AURASYNC ENTERPRISE</h2>", unsafe_allow_html=True)
    st.caption("Social-Native Mobile-First OS — Architettura a Doppia Navigazione")

with col_stats:
    st.markdown(
        f"<div style='text-align: right; padding-top: 8px; font-size: 14px; font-weight: 600;'>"
        f"👥 Persone: <span style='color:#FF4B4B;'>{st.session_state['visitatori']}</span> &nbsp;|&nbsp; "
        f"⚡ Utilizzi: <span style='color:#FF4B4B;'>{st.session_state['utilizzi']}</span>"
        f"</div>",
        unsafe_allow_html=True
    )

st.markdown("---")

# Barra di ricerca universale integrata
search_query = st.text_input(
    "🔍 Ricerca Universale di Sistema",
    placeholder="Cerca tra i 300 moduli, post o comandi rapidi..."
)

if search_query:
    st.success(indexing_msg := f"Motore di ricerca attivato per: '{search_query}' (Analisi cross-modulo in corso)")
    st.session_state["utilizzi"] += 1

st.markdown("---")

# Navigazione Bifurcata stabile
tab_social, tab_launcher = st.tabs([
    "💬 Bacheca Social (Feed Principale)", 
    "🚀 Launcher 50 Capitoli & 300 Moduli"
])

with tab_social:
    st.subheader("📰 Social Feed & Condivisione")
    
    # Form di pubblicazione pulito senza crash
    with st.form("social_post_form", clear_on_submit=True):
        autore = st.text_input("Il tuo Nome / Nickname", value="Utente Master")
        testo_nuovo = st.text_area("Condividi un aggiornamento con la rete...")
        invia = st.form_submit_button("Pubblica Post")
        
        if invia:
            if autore.strip() and testo_nuovo.strip():
                st.session_state["posts"].insert(0, {
                    "id": len(st.session_state["posts"]) + 1,
                    "utente": autore,
                    "testo": testo_nuovo,
                    "likes": 0,
                    "commenti": []
                })
                st.session_state["utilizzi"] += 1
                st.success("Post pubblicato con successo!")
            else:
                st.warning("Inserisci sia il nome che il testo del post.")

    st.markdown("### 🌐 Feed Attivo")
    for idx, post in enumerate(st.session_state["posts"]):
        with st.container():
            st.markdown(f"**👤 {post['utente']}**")
            st.write(post["col_testo"] if "col_testo" in post else post["testo"])
            
            col_like, col_info = st.columns([1, 4])
            with col_like:
                if st.button(f"👍 Mi piace ({post['likes']})", key=f"like_btn_{post['id']}_{idx}"):
                    post["likes"] += 1
            st.markdown("---")

with tab_launcher:
    st.subheader("📁 Master Launcher: Capitoli & Moduli")
    st.info("Seleziona un capitolo per avviare il modulo isolato corrispondente.")
    
    capitolo_selezionato = st.selectbox(
        "Seleziona Capitolo Operativo (1 - 50):",
        [f"Capitolo {i}: Moduli e Automazioni Avanzate" for i in range(1, 51)]
    )
    
    st.write(f"Hai selezionato: **{capitolo_selezionato}**")
    if st.button("Esegui Modulo Isolato"):
        st.session_state["utilizzi"] += 1
        st.success("Modulo avviato correttamente nell'ambiente sicuro.")
