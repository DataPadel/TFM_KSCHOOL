import base64
import pandas as pd
import seaborn as sns
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu

#Importar Utilidades App - Archivo Utilidades
from utilidades.utilidades import descargar_generar_archivo_palas_s3

#Importar utilidades App - Importar funciones utilizadas en el fichero principal de la app
from utilidades.app.utilidadaes_app import cargar_dataframes, analizador_graficos_datos, clasificador_golpes_padel

#Importar archivos de utilidades : utilidades y tratamiento_de_datos_formulario
from utilidades.tratamiento_de_datos.tratamiento_de_datos_palas import lectura_tratamiento_datos_palas, labelizar_columnas, calcular_scores, escalar_columnas, regresion_a_la_media_palas,ejecutar_una_vez

#Importar Formulario
from utilidades.app.formulario import formulario

#Importar Recomendador de Palas
from utilidades.app.recomendador_de_palas import recomendador_de_palas

#Import graficas de Palas
from utilidades.graficos.graficos_palas import graficas_palas

#Importar graficas de Formularios
from utilidades.graficos.graficos_formularios import graficas_formularios

# Configuración de la página para ancho completo
st.set_page_config(page_title="Plai Padel Pro", layout="wide")

# Función para convertir una imagen a Base64
def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Ruta de tu imagen local
image_path = "background_padel_image.jpg"  # Cambia esto por la ruta de tu imagen
encoded_image = get_base64_encoded_image(image_path)

# CSS dinámico para establecer la imagen como fondo
page_bg_img = f"""
<style>
[data-testid="stMainBlockContainer"]{{
    background: linear-gradient(rgba(0, 0, 0, 0.35), rgba(0, 0, 0, 0.35)),
        url("data:image/jpeg;base64,{encoded_image}");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

[data-testid="stMarkdownContainer"]{{
    position: relative; /* Asegura que el contenedor sea parte del contexto de apilamiento */
    z-index: 1; /* Coloca este contenedor por encima de la imagen de fondo */
}}
</style>
"""

# Aplicar CSS personalizado
#st.markdown(page_bg_img, unsafe_allow_html=True)

# Inicializar el estado global para controlar la navegación
if "menu_option" not in st.session_state:
    st.session_state["menu_option"] = "Formulario"

if "datos_procesados" not in st.session_state:
    st.session_state["datos_procesados"] = False  # Indica si los datos ya fueron procesados


# Funcion para cargar y preprocesar los datos iniciales

def cargar_preprocesar_datos_iniciales():
    """Preprocesa los datos iniciales solo una vez."""
    if not st.session_state.get("datos_procesados", False):
        
        try:

            # Paso 1: Cargar DataFrames
            df_form, df_palas = cargar_dataframes()
            st.session_state["df_form"] = df_form
            st.session_state["df_palas"] = df_palas

            # Paso 1: Lectura y tratamiento de datos
            descargar_generar_archivo_palas_s3()
            ejecutar_una_vez(lectura_tratamiento_datos_palas, "datos_leidos")

            # Paso 2: Procesamiento adicional (labelización, cálculos, etc.)
            ejecutar_una_vez(labelizar_columnas, "labelizacion_realizada")
            ejecutar_una_vez(calcular_scores, "scores_calculados")
            ejecutar_una_vez(escalar_columnas, "columnas_escaladas")
            ejecutar_una_vez(regresion_a_la_media_palas, "regresion_aplicada")

            # Marcar como procesado
            st.session_state["datos_procesados"] = True

        except Exception as e:
            st.error(f"Error durante el preprocesamiento: {e}")


# Carga de dataframes y preprocesamiento de datos
cargar_preprocesar_datos_iniciales()


# MENU LATERAL
with st.sidebar:
    opcion_seleccionada = option_menu(
        menu_title="Plai Padel Pro",
        options=["Formulario", "Recomendador de Pala", "Graficas de palas","Graficas de Formularios","Analizador de Graficas/Datos"], 
        icons=["pencil-fill", "bar-chart-fill", "graph-up","graph-up","table"], 
        menu_icon="cast",
        default_index=0,
        key="menu_option"
    )
    
    
# OPCIONES DE MENU

if st.session_state["menu_option"] == "Formulario":
    formulario()
elif st.session_state["menu_option"] == "Recomendador de Pala":
    recomendador_de_palas()
elif st.session_state["menu_option"] == "Graficas de palas": 
    graficas_palas()
elif st.session_state["menu_option"] == "Graficas de Formularios": 
    graficas_formularios()
elif st.session_state["menu_option"] == "Analizador de Graficas/Datos": 
    analizador_graficos_datos()
elif st.session_state["menu_option"] == "Clasificador de Golpes de Padel": 
    clasificador_golpes_padel()