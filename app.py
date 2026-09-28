import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURAZIONE E STATO DI SESSIONE ---
if "piano_attivo" not in st.session_state:
    st.session_state.piano_attivo = "Free"
if "conteggio_analisi" not in st.session_state:
    st.session_state.conteggio_analisi = 0
if "lista_recensioni" not in st.session_state:
    st.session_state.lista_recensioni = []

st.title("Split & Save AI")
st.markdown("Il tuo direttore finanziario personale basato sull'intelligenza artificiale.")

# --- BARRA LATERALE: GESTIONE PIANI E ABBONAMENTI ---
st.sidebar.header("💳 Gestione Piani")
st.sidebar.write(f"Piano attuale: **{st.session_state.piano_attivo}**")

st.sidebar.markdown("---")
st.sidebar.subheader("Scegli il tuo piano:")

if st.sidebar.button("Attiva Smart (€4,99)"):
    st.session_state.piano_attivo = "Smart"
    st.session_state.conteggio_analisi = 0
    st.sidebar.success("Piano Smart attivato!")

if st.sidebar.button("Attiva Pro (€9,99)"):
    st.session_state.piano_attivo = "Pro"
    st.session_state.conteggio_analisi = 0
    st.sidebar.success("Piano Pro attivato!")

if st.sidebar.button("Attiva Unlimited (€14,99 / 30gg)"):
    st.session_state.piano_attivo = "Unlimited"
    st.session_state.conteggio_analisi = 0
    st.sidebar.success("Piano Unlimited attivato!")

# --- DEFINIZIONE REGOLE PER PIANO ---
limiti_config = {
    "Free": {"limite": 2, "tipo": "giornaliere", "funzioni": "Analisi completa, riepilogo e punti critici"},
    "Smart": {"limite": 15, "tipo": "settimanali", "funzioni": "Solo analisi e riepilogo budget (senza punti critici)"},
    "Pro": {"limite": 25, "tipo": "settimanali", "funzioni": "Analisi, riepilogo e punti critici"},
    "Unlimited": {"limite": 9999, "tipo": "illimitate (30 giorni)", "funzioni": "Tutto illimitato e sbloccato"}
}

info_piano = limiti_config[st.session_state.piano_attivo]
st.info(f"Stai usando il piano **{st.session_state.piano_attivo}**: {info_piano['limite']} analisi {info_piano['tipo']}. \n\nFunzionalità incluse: *{info_piano['funzioni']}*")

# --- SCELTA DELLA MODALITA' DI INPUT ---
modalita = st.radio(
    "Come vuoi inserire le tue spese o notifiche?",
    ["Copia e Incolla Testo / Notifiche", "Carica Screenshot (Banca / Scontrino)"]
)

user_input = None
immagine_caricata = None

if modalita == "Copia e Incolla Testo / Notifiche":
    user_input = st.text_area("Incolla qui la lista delle spese o il testo delle notifiche bancarie:", height=150)
else:
    immagine_caricata = st.file_uploader("Carica lo screenshot della notifica bancaria o dello scontrino", type=["png", "jpg", "jpeg"])

# --- PULSANTE DI ANALISI ---
if st.button("Analizza con IA", type="primary"):
    
    # Controllo dei limiti in base al piano
    if st.session_state.conteggio_analisi >= info_piano["limite"]:
        st.error(f"🚫 Hai esaurito le analisi disponibili per il tuo piano ({st.session_state.piano_attivo})!")
        st.warning("Fai un upgrade dal menu laterale per sbloccare più analisi o passare al piano illimitato.")
    else:
        ha_input = (modalita == "Copia e Incolla Testo / Notifiche" and user_input and user_input.strip() != "") or \
                   (modalita == "Carica Screenshot (Banca / Scontrino)" and immagine_caricata is not None)
        
        if not ha_input:
            st.warning("Per favore, inserisci del testo o carica un'immagine prima di procedere!")
        else:
            st.session_state.conteggio_analisi += 1
            
            with st.spinner("Analisi finanziaria in corso con l'intelligenza artificiale..."):
                try:
                    genai.configure(api_key=st.secrets.get("CENTRAL_API_KEY", ""))
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # Regolazione del prompt in base alle restrizioni del piano Smart
                    if st.session_state.piano_attivo == "Smart":
                        prompt_istruzioni = "Fai solo un'analisi di base e il riepilogo del budget. Non includere i punti critici o suggerimenti avanzati."
                    else:
                        prompt_istruzioni = "Fai un'analisi dettagliata, riepilogo del budget, punti critici e proposta di ottimizzazione completa."

                    if modalita == "Carica Screenshot (Banca / Scontrino)" and immagine_caricata:
                        img = Image.open(immagine_caricata)
                        prompt = [f"Analizza questo screenshot di una notifica bancaria o scontrino. {prompt_istruzioni}", img]
                        risposta = model.generate_content(prompt)
                    else:
                        prompt = f"{prompt_istruzioni}\n\nLista spese:\n{user_input}"
                        risposta = model.generate_content(prompt)
                    
                    st.success("Analisi completata con successo!")
                    st.write(risposta.text)
                    
                except Exception as e:
                    st.error(f"Errore durante l'analisi: {e}")

# --- SEZIONE RECENSIONI E COMMUNITY (PUBBLICA) ---
st.markdown("---")
st.subheader("⭐ Valuta Split & Save AI")

with st.form("form_recensione", clear_on_submit=True):
    voto = st.slider("Seleziona una valutazione (da 1 a 5 stelle):", 1, 5, 5)
    commento = st.text_area("Lascia un commento o un feedback per la community:")
    inviato = st.form_submit_button("Invia recensione")
    
    if inviato:
        if commento.strip() == "":
            st.warning("Per favore, inserisci un breve commento prima di inviare.")
        else:
            st.session_state.lista_recensioni.append({"voto": voto, "commento": commento})
            st.success("Grazie! La tua recensione è stata pubblicata nella bacheca della community.")

# Bacheca pubblica visibile a tutti gli utenti
if len(st.session_state.lista_recensioni) > 0:
    st.markdown("---")
    st.subheader("💬 Bacheca Recensioni della Community")
    
    media_voti = sum(r["voto"] for r in st.session_state.lista_recensioni) / len(st.session_state.lista_recensioni)
    st.metric(label="Valutazione Media", value=f"{media_voti:.1f} / 5.0 ⭐")
    
    for rec in reversed(st.session_state.lista_recensioni):
        stelle = "⭐" * rec["voto"]
        st.info(f"{stelle}\n\n\"{rec['commento']}\"")
