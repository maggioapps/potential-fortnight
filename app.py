import streamlit as st

st.set_page_config(
    page_title="AURASYNC OS — Ultimate Edition",
    page_icon="⚡",
    layout="wide"
)

if "posts" not in st.session_state:
    st.session_state["posts"] = [
        {
            "id": 1,
            "utente": "AuraSync Community",
            "testo": "Benvenuti nella bacheca ufficiale di AURASYNC! Feed principale attivo.",
            "likes": 15,
            "commenti": ["Ottimo lavoro!"],
            "condivisibile": True
        }
    ]

if "visitatori" not in st.session_state:
    st.session_state["visitatori"] = 35
if "utilizzi" not in st.session_state:
    st.session_state["utilizzi"] = 120

col_logo, col_counter = st.columns([3, 1])

with col_logo:
    st.markdown("<h1 style='margin: 0; padding: 0;'>AURASYNC</h1>", unsafe_allow_html=True)

with col_counter:
    st.markdown(
        f"<div style='text-align: right; padding-top: 10px; font-size: 13px; color: #666;'>"
        f"👥 <b>{st.session_state['visitatori']}</b> Persone &nbsp;|&nbsp; ⚡ <b>{st.session_state['utilizzi']}</b> Utilizzi"
        f"</div>", 
        unsafe_allow_html=True
    )

st.markdown("---")

query_universale = st.text_input(
    "🔍 Ricerca Universale (Cerca tra i 300 moduli o fai una domanda):",
    placeholder="Es. Media ponderata, Sblocco lavandino..."
)

if query_universale:
    st.info(f"Risultati rapidi per: **{query_universale}**")
    st.session_state["utilizzi"] += 1

st.markdown("---")

nav_principale = st.radio(
    "Navigazione Sistema:",
    ["💬 Bacheca Social (Home)", "📁 Cartella 50 Capitoli & 300 Moduli"],
    horizontal=True
)

st.markdown("---")

if nav_principale == "💬 Bacheca Social (Home)":
    st.subheader("💬 Bacheca Pubblica")
    
    with st.form("form_post", clear_on_submit=True):
        nome_autore = st.text_input("Il tuo Nome / Nickname:")
        contenuto_post = st.text_area("A cosa stai pensando?")
        pubblica = st.form_submit_button("Pubblica Post")
        
        if pubblica and nome_autore and contenuto_post:
            st.session_state["posts"].insert(0, {
                "id": len(st.session_state["posts"]) + 1,
                "utente": nome_autore,
                "testo": contenuto_post,
                "likes": 0,
                "commenti": [],
                "condivisibile": True
            })
            st.rerun()

    st.markdown("### 📰 Feed Recenti")
    for post in st.session_state["posts"]:
        st.markdown(f"**👤 {post['utente']}**")
        st.write(post["testo"])
        if st.button(f"👍 {post['likes']}", key=f"like_{post['id']}"):
            post["likes"] += 1
            st.rerun()
        st.markdown("---")
else:
    st.subheader("📁 Cartella Master: I 50 Capitoli & 300 Moduli")
    st.write("Selettore dei moduli isolati attivo.")
