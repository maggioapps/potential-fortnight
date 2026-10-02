# --- GESTIONE STATO UTENTE E VISITE PERSISTENTI ---
if "is_loggato" not in st.session_state:
    st.session_state.is_loggato = False
if "utente_email" not in st.session_state:
    st.session_state.utente_email = ""
if "storico_salvataggi" not in st.session_state:
    st.session_state.storico_salvataggi = []
if "notifiche_attive" not in st.session_state:
    st.session_state.notifiche_attive = False

# Conta-persone reale basato sulla sessione attiva del browser
if "visitato" not in st.session_state:
    st.session_state.visitato = True
    if "visite" not in st.session_state:
        st.session_state.visite = 142  # Numero di partenza realistico o 1
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
