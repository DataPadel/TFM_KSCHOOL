import os
import base64
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu

# Importar módulos personalizados
from utilidades.app.formulario import formulario
from utilidades.graficos.graficos_palas import graficas_palas
from utilidades.app.recomendador_de_palas import recomendador_de_palas
from utilidades.utilidades import descargar_archivo_palas_formulario_s3
from utilidades.graficos.graficos_formularios import graficas_formularios
from utilidades.tratamiento_de_datos.utilidades_tratamiento_de_datos_palas import ejecutar_una_vez
from utilidades.tratamiento_de_datos.tratamiento_de_datos_palas import (
    lectura_tratamiento_datos_palas, labelizar_columnas, calcular_scores, 
    escalar_columnas, regresion_a_la_media_palas
)
from utilidades.tratamiento_de_datos.tratamiento_de_datos_formulario import (
    procesar_datos_formulario_csv, crear_dataframes_con_scores, 
    procesar_scores_y_guardar, regresion_a_la_media_formulario
)

# Configuración de la página para ancho completo
st.set_page_config(page_title="Play Padel Pro", layout="wide")

# Función para convertir una imagen a Base64
def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Ruta del logo y conversión a Base64
logo_path = "play_padel_pro_logo.jpg"  # Cambia esto por la ruta de tu logo
encoded_logo = get_base64_encoded_image(logo_path)

# CSS para insertar el logo en el menú lateral
logo_html = f"""
<style>
.sidebar-logo {{
    text-align: center;
    margin-bottom: 20px;
}}
.sidebar-logo img {{
    width: 250px;
    height: auto;
}}
</style>
<div class="sidebar-logo">
    <img src="data:image/jpeg;base64,{encoded_logo}" alt="Plai Padel Pro Logo">
</div>
"""

# Aplicar CSS personalizado al menú lateral
st.sidebar.markdown(logo_html, unsafe_allow_html=True)

# Inicializar el estado global para controlar la navegación
if "menu_option" not in st.session_state:
    st.session_state["menu_option"] = "Formulario"

if "datos_procesados" not in st.session_state:
    st.session_state["datos_procesados"] = False  # Indica si los datos ya fueron procesados

# Función para cargar y preprocesar los datos iniciales (sin cambios)
def cargar_preprocesar_datos_iniciales():
    """Preprocesa los datos iniciales solo una vez."""
    if not st.session_state.get("datos_procesados", False):
        try:
            # Paso 1: Lectura de palas y formulario
            descargar_archivo_palas_formulario_s3()

            # Paso 2: Tratamiento de Datos Palas
            ejecutar_una_vez(lectura_tratamiento_datos_palas, "datos_leidos")
            ejecutar_una_vez(labelizar_columnas, "Labelizacion de Palas Realizada")
            ejecutar_una_vez(calcular_scores, "Scores de Palas Calculados")
            ejecutar_una_vez(escalar_columnas, "Columnas de Palas Escaladas")
            ejecutar_una_vez(regresion_a_la_media_palas, "Regresion de Palas Aplicada")
            print("Procesamiento de Palas Completado. Fichero df_scaled_palas_3.0 generado")
            
            # Paso 3: Tratamiento de Datos Formulario
            ejecutar_una_vez(procesar_datos_formulario_csv, 'Label Mapping Aplicado')
            ejecutar_una_vez(crear_dataframes_con_scores, 'Dataframe con Scores Creado')
            ejecutar_una_vez(procesar_scores_y_guardar, 'Dataframe con Scores Procesado')
            ejecutar_una_vez(regresion_a_la_media_formulario, "Regresion a la media Formulario Realizada")
            
            # Validar si el archivo df_scaled_formularios_3.0.csv se creó correctamente
            output_file = 'df_scaled_formularios_3.0.csv'
            if not os.path.exists(output_file):
                raise FileNotFoundError(f"El archivo '{output_file}' no se creó correctamente.")

            print("Procesamiento de Formulario Completado. Fichero df_scaled_formularios_3.0 generado")

            # Marcar como procesado
            st.session_state["datos_procesados"] = True

        except FileNotFoundError as e:
            st.error(f"Archivo no encontrado: {e}")
        except Exception as e:
            st.error(f"Error durante el preprocesamiento: {e}")

# Carga de dataframes y preprocesamiento de datos (sin cambios)
cargar_preprocesar_datos_iniciales()

# MENU LATERAL CON LOGO Y OPCIONES
with st.sidebar:
    opcion_seleccionada = option_menu(
        menu_title=None,  # Eliminar el título predeterminado del menú lateral
        options=["Formulario", "Recomendador de Pala", "Graficas de palas", "Graficas de Formularios"], 
        icons=["pencil-fill", "bar-chart-fill", "graph-up", "graph-up"], 
        menu_icon="cast",
        default_index=0,
        key="menu_option"
    )

# OPCIONES DE MENÚ (sin cambios)
if st.session_state["menu_option"] == "Formulario":
    formulario()
elif st.session_state["menu_option"] == "Recomendador de Pala":
    recomendador_de_palas()
elif st.session_state["menu_option"] == "Graficas de palas": 
    graficas_palas()
elif st.session_state["menu_option"] == "Graficas de Formularios": 
    graficas_formularios()
