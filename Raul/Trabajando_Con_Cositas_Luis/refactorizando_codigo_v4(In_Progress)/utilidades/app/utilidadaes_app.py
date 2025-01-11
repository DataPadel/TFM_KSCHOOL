import time
import pandas as pd
import streamlit as st
from pygwalker.api.streamlit import StreamlitRenderer

# Funciones relacionada con la funcionalidad FORMULARIO

# Función para marcar que el formulario ha sido modificado
def actualizar_estado_formulario():
    st.session_state["formulario_modificado"] = True
    st.session_state["formulario_enviado"] = False  # Reinicia el estado de enviado

@st.cache_data
def cargar_dataframes():
    progress_text = "Cargando DataFrames. Por favor, espere..."
    progress_bar = st.progress(0, text=progress_text)

    # Paso 1: Cargar el primer DataFrame
    progress_bar.progress(25, text=f"{progress_text} 25% completado")
    df_form = pd.read_csv('df_scaled_formularios_3.0.csv')

    # Paso 2: Cargar el segundo DataFrame
    progress_bar.progress(75, text=f"{progress_text} 75% completado")
    df_palas = pd.read_csv('df_scaled_palas_3.0.csv')

    # Finalización
    progress_bar.progress(100, text=f"{progress_text} 100% completado")

    # Esperar 2 segundos antes de eliminar la barra de progreso
    time.sleep(2)
    
    # Actualizar la barra con un espacio vacío para "ocultarla"
    progress_bar.empty()

    return df_form, df_palas


# Función para obtener el DataFrame actualizado desde el estado global
def obtener_dataframe_actualizado():
    if "df_form" in st.session_state:
        return st.session_state["df_form"]
    else:
        df_form, _ = cargar_dataframes()
        st.session_state["df_form"] = df_form  # Asegurar que se guarde en session_state
        return df_form
    
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Programa Tipo Tableau que permite analizar datos graficamente(Pygwalker)

def analizador_graficos_datos():
    st.title("Analizador Graficos/Datos (Tipo Tableau)")

    # Cargar un DataFrame de ejemplo (puedes usar tus propios datos)
    try:
        df = pd.read_csv('PNpalas_DF_2_procesado.csv')  # Cambia la ruta según tus datos
    except FileNotFoundError:
        st.error("No se encontró el archivo 'bike_sharing_dc.csv'. Por favor, verifica la ruta.")
        return

    # Inicializar Pygwalker Renderer
    @st.cache_resource
    def get_pyg_renderer(dataframe: pd.DataFrame) -> "StreamlitRenderer":
        return StreamlitRenderer(dataframe)

    renderer = get_pyg_renderer(df)

    # Explorar los datos con Pygwalker
    renderer.explorer()
    

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Clasificador de Golpes de Padel que a partir de una o varias imagenes nos permite distinguir el tipo de golpe y si esta bien o mal ejecutado

def clasificador_golpes_padel():
    return "Clasificador de Golpes de Padel"