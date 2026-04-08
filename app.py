import streamlit as st
import pandas as pd

# Configuración de la interfaz (Layout ancho para mejor lectura de sentencias)
st.set_page_config(page_title="RomoLegal - Inteligencia Jurídica", page_icon="⚖️", layout="wide")

# Estilos visuales personalizados (Sobriedad y elegancia para el Tribunal)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stSidebar { background-color: #1a237e; color: white; }
    .titulo { color: #1a237e; font-family: 'Georgia', serif; text-align: center; font-weight: bold; margin-bottom: 20px; }
    .card { border-left: 6px solid #1a237e; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .sentencia-id { color: #1a237e; font-size: 20px; font-weight: bold; margin-bottom: 5px; }
    .meta { color: #555; font-size: 14px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def cargar_datos():
    # ID de tu Google Sheet
    sheet_id = "1idun_9zH-y57FdiqhNHxcnY4bA8T2iw7"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(url)
    # Limpieza básica de datos
    df['text'] = df['text'].astype(str).fillna('')
    df['anio'] = pd.to_numeric(df['anio'], errors='coerce').fillna(0).astype(int)
    return df

try:
    df = cargar_datos()

    # --- BARRA LATERAL (SIDEBAR) PARA FILTROS TÉCNICOS ---
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2821/2821637.png", width=100)
    st.sidebar.title("Filtros de Especialidad")
    
    # Filtro por Magistrado Ponente
    lista_magistrados = ["Todos los Magistrados"] + sorted(df['Magistrado Ponente'].unique().tolist())
    mag_seleccionado = st.sidebar.selectbox("Filtrar por Ponente:", lista_magistrados)

    # Filtro por Rango Cronológico
    anio_min, anio_max = int(df['anio'].min()), int(df['anio'].max())
    rango_anio = st.sidebar.slider("Rango de Años:", anio_min, anio_max, (anio_min, anio_max))

    # --- CUERPO PRINCIPAL ---
    st.markdown("<h1 class='titulo'>🏛️ Buscador de Jurisprudencia RomoLegal</h1>", unsafe_allow_html=True)
    
    # Campo de búsqueda con la instrucción específica que pediste
    busqueda = st.text_input(
        "Ingrese conceptos jurídicos:", 
        placeholder="Para una búsqueda específica, combine términos con '+'. Ej: estabilidad laboral + embarazo"
    )
    
    st.caption("💡 Tip: El sistema buscará sentencias que contengan TODOS los términos ingresados.")

    # Lógica de filtrado dinámico
    df_filtrado = df.copy()

    # 1. Aplicar filtros de la barra lateral
    if mag_seleccionado != "Todos los Magistrados":
        df_filtrado = df_filtrado[df_filtrado['Magistrado Ponente'] == mag_seleccionado]
    
    df_filtrado = df_filtrado[(df_filtrado['anio'] >= rango_anio[0]) & (df_filtrado['anio'] <= rango_anio[1])]

   # 2. Aplicar lógica de búsqueda cruzada (INTERSECCIÓN OBLIGATORIA)
    if busqueda:
        # Limpiamos la cadena: quitamos el '+' y dividimos por espacios
        # Esto permite que busque tanto 'estabilidad + embarazo' como 'estabilidad embarazo'
        terminos = busqueda.replace('+', ' ').split()
        
        for t in terminos:
            t = t.strip()
            if t:
                # La magia ocurre aquí: cada ciclo reduce el DataFrame 
                # dejando solo lo que contiene el término actual Y los anteriores.
                df_filtrado = df_filtrado[df_filtrado['text'].str.contains(t, case=False, na=False)]

    # --- MOSTRAR RESULTADOS (LÓGICA MEJORADA) ---
    
    # Solo mostramos resultados si el usuario ha escrito algo o ha filtrado por un magistrado específico
    if busqueda or mag_seleccionado != "Todos los Magistrados":
        if not df_filtrado.empty:
            st.success(f"Análisis completado: Se hallaron {len(df_filtrado)} providencias coincidentes.")
            
            for i, fila in df_filtrado.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="card">
                        <div class="sentencia-id">Sentencia {fila['Sentencia']}</div>
                        <div class="meta">
                            <b>Magistrado Ponente:</b> {fila['Magistrado Ponente']} | 
                            <b>Año de la providencia:</b> {fila['anio']}
                        </div>
                        <p style='font-size: 15px; line-height: 1.6; color: #333;'>
                            {fila['text'][:450]}...
                        </p>
                        <a href="{fila['url']}" target="_blank" style="color: #1a237e; font-weight: bold; text-decoration: none; border: 1px solid #1a237e; padding: 5px 10px; border-radius: 5px;">
                            📂 Ver providencia completa
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("No se encontraron registros que coincidan con la combinación de términos y filtros seleccionados.")
    else:
        # Mensaje de bienvenida cuando la app está limpia
        st.info("👋 Bienvenido a RomoLegal. Ingrese un concepto jurídico arriba o use los filtros laterales para comenzar el análisis.")

except Exception as e:
    st.error(f"Error en la conexión con la base de datos: {e}")
