import time
import pandas as pd
import streamlit as st
from pygwalker.api.streamlit import StreamlitRenderer

# Funciones relacionada con la funcionalidad FORMULARIO

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


def obtener_dataframe_actualizado(forzar_recarga=False):
    """
    Obtiene el DataFrame actualizado desde session_state o lo carga desde el archivo CSV si no existe.
    
    Args:
        forzar_recarga (bool): Si es True, fuerza la recarga del DataFrame desde el archivo CSV.
        
    Returns:
        pd.DataFrame: El DataFrame actualizado.
    """
    # Si se solicita una recarga, eliminar df_form del estado de sesión
    if forzar_recarga and "df_form" in st.session_state:
        del st.session_state["df_form"]

    # Verificar si df_form ya está en session_state
    if "df_form" in st.session_state:
        return st.session_state["df_form"]
    else:
        # Cargar los datos desde el archivo
        df_form, _ = cargar_dataframes()

        # Validar si hay valores faltantes significativos
        if df_form.empty or df_form.isnull().mean().mean() > 0.5:  # Más del 50% NaN
            raise ValueError("El DataFrame cargado contiene demasiados valores faltantes.")

        # Guardar en session_state
        st.session_state["df_form"] = df_form
        return df_form

    
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Programa Tipo Tableau que permite analizar datos graficamente(Pygwalker)

def analizador_graficos_datos():
    st.title("Analizador Graficos/Datos (Tipo Tableau)")

    # Cargar un DataFrame de ejemplo (puedes usar tus propios datos)
    try:
        df = pd.read_csv('df_scaled_formularios_3.0.csv')  # Cambia la ruta según tus datos
    except FileNotFoundError:
        st.error("No se encontró el archivo. Por favor, verifica la ruta.")
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