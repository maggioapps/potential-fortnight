import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Split & Save AI", layout="centered")

# Inserisci qui la tua chiave API centralizzata di Gemini
CENTRAL_API_KEY = st.secrets["GEMINI_API_KEY"]

st.title("Split & Save AI")
st.markdown("Il tuo direttore finanziario personale.")

# Menu laterale con i 4 piani
st.sidebar.title("Scegli il tuo Piano")
piano = st.sidebar.selectbox(
    "Seleziona il livello:", 
    [
        "Free (Gratuito)", 
        "Smart (€4.99/mese - 10gg prova)", 
        "Pro (€9.99/mese - 10gg prova)", 
        "Ultra (€14.99/mese - 10gg prova)"
    ]
)

# ----------------- 1. VERSIONE FREE -----------------
if piano == "Free (Gratuito)":
    st.info("Stai usando il piano **Free**: massimo 3 analisi al giorno.")
    user_input = st.text_area("Incolla qui la lista delle spese:", height=150)
    
    if st.button("Analizza (Free)", type="primary"):
        if not user_input.strip():
            st.warning("Inserisci qualche spesa!")
        else:
            try:
                genai.configure(api_key=CENTRAL_API_KEY)
                model = genai.GenerativeModel("gemini-3.8-flash")
                response = model.generate_content(user_input)
                
                st.success("Analisi completata!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Errore: {e}")

# ----------------- 2. VERSIONE SMART (€4.99) -----------------
elif piano == "Smart (€4.99/mese - 10gg prova)":
    st.success("✨ Piano SMART: Analisi illimitate e categorizzazione!")
    st.markdown("Goditi **10 giorni di prova gratuita**, poi 4.99€/mese (disdici quando vuoi).")
    st.markdown("[👉 Attiva la prova gratuita Smart su Stripe](https://tuo-link-stripe-smart.com)")
    
    email = st.text_input("Inserisci la tua email (Smart):")
    if email:
        user_input = st.text_area("Incolla le spese (Smart):", height=150)
        if st.button("Analizza con Smart AI"):
            try:
                genai.configure(api_key=CENTRAL_API_KEY)
                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(f"Fai un'analisi e categorizzazione di queste spese: {user_input}")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Errore: {e}")

# ----------------- 3. VERSIONE PRO (€9.99) -----------------
elif piano == "Pro (€9.99/mese - 10gg prova)":
    st.warning("🚀 Piano PRO: Consigli avanzati di risparmio!")
    st.markdown("Goditi **10 giorni di prova gratuita**, poi 9.99€/mese.")
    st.markdown("[👉 Attiva la prova gratuita Pro su Stripe](https://tuo-link-stripe-pro.com)")
    
    email = st.text_input("Inserisci la tua email (Pro):")
    if email:
        user_input = st.text_area("Incolla le spese (Pro):", height=150)
        if st.button("Analizza con Pro AI"):
            try:
                genai.configure(api_key=CENTRAL_API_KEY)
                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(f"Fai un'analisi finanziaria approfondita e dai consigli di risparmio per queste spese: {user_input}")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Errore: {e}")

# ----------------- 4. VERSIONE ULTRA (€14.99) -----------------
elif piano == "Ultra (€14.99/mese - 10gg prova)":
    st.error("👑 Piano ULTRA: Potenza massima e report dettagliati!")
    st.markdown("Goditi **10 giorni di prova gratuita**, poi 14.99€/mese.")
    st.markdown("[👉 Attiva la prova gratuita Ultra su Stripe](https://tuo-link-stripe-ultra.com)")
    
    email = st.text_input("Inserisci la tua email (Ultra):")
    if email:
        user_input = st.text_area("Incolla le spese (Ultra):", height=150)
        if st.button("Analizza con Ultra AI"):
            try:
                genai.configure(api_key=CENTRAL_API_KEY)
                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(f"Fai un report finanziario di livello professionale, con piano di budget e ottimizzazione avanzata per queste spese: {user_input}")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Errore: {e}")
