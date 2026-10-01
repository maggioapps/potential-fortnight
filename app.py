import streamlit as st

st.set_page_config(
    page_title="AuraSync OS — Full Edition",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #111;
        margin-bottom: 0px;
    }
    .sub-text {
        color: #666;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">⚡ AuraSync OS — Centro di Controllo</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Esecuzione Modulo Isolato | Lingua attiva: Italiano (it)</div>', unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### 🖥️ Dashboard Zero-Click & Control Center")
    st.write("Panoramica rapida del tuo ecosistema operativo personale.")
    
    st.info("💡 **Stato del Sistema**: Online e pronto all'uso. Seleziona un modulo o naviga nella bacheca social.")

with col2:
    st.metric(label="Moduli Totali", value="300", delta="Disponibili")

st.markdown("---")

# Sezioni di navigazione principali
tab_feed, tab_moduli = st.tabs(["💬 Bacheca Social", "🚀 Launcher 300 Moduli"])

with tab_feed:
    st.subheader("Bacheca Social & Feed Attivo")
    st.write("Spazio di condivisione e aggiornamenti in tempo reale.")
    
    # Area inserimento post
    with st.form("form_bacheca"):
        autore = st.text_input("Il tuo nome / nickname")
        messaggio = st.text_area("Scrivi un pensiero o condividi un modulo...")
        invia = st.form_submit_button("Pubblica sulla Bacheca")
        
        if invia and autore and messaggio:
            st.success(f"Pubblicato con successo da {autore}!")

    st.markdown("---")
    st.markdown("### Ultimi Post della Community")
    st.info("🔹 **AuraSync Bot**: Sistema operativo mobile-first aggiornato e sincronizzato al 100%.")

with tab_moduli:
    st.subheader("Archivio Capitoli & Moduli")
    st.write("Seleziona i moduli operativi per il calcolo, l'analisi o l'automazione.")
    
    capitolo = st.selectbox("Seleziona Capitolo (1 - 50):", [f"Capitolo {i}" for i in range(1, 51)])
    st.write(Hai selezionato: **{capitolo}**)
    
    if st.button("Esegui Modulo"):
        st.success("Modulo avviato correttamente.")
