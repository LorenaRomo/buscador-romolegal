import streamlit as st
import pandas as pd

# Configuración estética RomoLegal
st.set_page_config(page_title="Buscador RomoLegal", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .titulo { color: #1a237e; font-family: 'Georgia', serif; text-align: center; }
    .stButton>button { background-color: #1a237e; color: white; }
    .card { border-left: 5px solid #1a237e; padding: 15px; background: white; box-shadow: 2px 2px 5px #eee; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='titulo'>🏛️ Buscador de Jurisprudencia RomoLegal</h1>", unsafe_allow_html=True)

@st.cache_data
def cargar_datos():
    # ID extraído de tu enlace de Sheets
    sheet_id = "1idun_9zH-y57FdiqhNHxcnY4bA8T2iw7"
    # URL para que Python lo descargue como CSV automáticamente
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(url)
    df['text'] = df['text'].astype(str).fillna('')
    return df

try:
    df = cargar_datos()
    tema = st.text_input("Ingrese el concepto jurídico (Ej: Habeas Data, eutanasia, consulta previa, estabilidad laboral):")
    
    if tema:
        resultados = df[df['text'].str.contains(tema, case=False, na=False)]
        st.success(f"Se hallaron {len(resultados)} coincidencias en la base de datos.")
        
        for i, fila in resultados.iterrows():
            st.markdown(f"""
            <div class="card">
                <h4>Sentencia {fila['Sentencia']}</h4>
                <p><b>Ponente:</b> {fila['Magistrado Ponente']} | <b>Año:</b> {fila['anio']}</p>
                <p style='font-size: 14px;'>{fila['text'][:350]}...</p>
                <a href="{fila['url']}" target="_blank">Ver providencia completa</a>
            </div>
            """, unsafe_allow_html=True)
except Exception as e:
    st.error("Error al conectar con la base de datos de Google Sheets. Verifique los permisos de compartir.")
