import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Ripartizione Categorie", layout="wide")

st.title("Ripartizione Categorie e Analisi Dati")

# Dati di esempio per i grafici
df = pd.DataFrame({
    "Categoria": ["Elettronica", "Abbigliamento", "Casa", "Sport", "Alimentari"],
    "Valore": [4500, 3200, 2100, 1800, 3900],
    "Quantita": [120, 250, 90, 110, 310]
})

def mostra_grafico_compatto():
    st.subheader("Grafico di Ripartizione per Valore")
    
    # Creazione del grafico a barre con Plotly Express
    fig = px.bar(
        df, 
        x="Categoria", 
        y="Valore", 
        color="Categoria",
        title="Valore per Categoria di Prodotto"
    )
    
    # IMPORTANTE: Aggiunta di una chiave univoca (key) per evitare il conflitto StreamlitDuplicateElementId
    st.plotly_chart(fig, use_container_width=True, key="grafico_valore_categoria")

# Esecuzione della funzione
mostra_grafico_compatto()

st.divider()

def mostra_secondo_grafico():
    st.subheader("Grafico delle Quantità")
    
    fig2 = px.pie(
        df, 
        names="Categoria", 
        values="Quantita", 
        title="Distribuzione Quantità"
    )
    
    # Seconda chiave univoca per il grafico a torta
    st.plotly_chart(fig2, use_container_width=True, key="grafico_torta_quantita")

mostra_secondo_grafico()
```eof

Il codice aggiornato è pronto! Ho corretto il problema aggiungendo le chiavi (`key`) univoche a tutti i componenti Plotly in modo che Streamlit non generi più conflitti di ID duplicati. Fammi sapere se hai bisogno di altre modifiche!
