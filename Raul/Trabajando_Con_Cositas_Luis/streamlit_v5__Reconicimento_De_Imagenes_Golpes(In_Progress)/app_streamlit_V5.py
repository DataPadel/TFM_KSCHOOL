import os
import base64
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu


#Importar Formulario
from utilidades.app.formulario import formulario

#Import graficas de Palas
from utilidades.graficos.graficos_palas import graficas_palas

#Importar Recomendador de Palas
from utilidades.app.recomendador_de_palas import recomendador_de_palas

#Importar Utilidades App - Archivo Utilidades
from utilidades.utilidades import descargar_archivo_palas_formulario_s3

#Importar graficas de Formularios
from utilidades.graficos.graficos_formularios import graficas_formularios

from utilidades.tratamiento_de_datos.utilidades_tratamiento_de_datos_palas import ejecutar_una_vez

#Importar archivos de utilidades : utilidades y tratamiento_de_datos_palas
from utilidades.tratamiento_de_datos.tratamiento_de_datos_palas import lectura_tratamiento_datos_palas, labelizar_columnas, calcular_scores, escalar_columnas, regresion_a_la_media_palas

#Importar archivos de utilidades : utilidades y tratamiento_de_datos_formularios
from utilidades.tratamiento_de_datos.tratamiento_de_datos_formulario import procesar_datos_formulario_csv,crear_dataframes_con_scores,procesar_scores_y_guardar,regresion_a_la_media_formulario


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

            ejecutar_una_vez(regresion_a_la_media_formulario, "Regresion a la media Formulario Realizada")
            print("Procesamiento de Formulario Completado. Fichero df_scaled_formularios_3.0 generado")

            # Marcar como procesado
            st.session_state["datos_procesados"] = True
            

        except FileNotFoundError as e:
            st.error(f"Archivo no encontrado: {e}")
        except Exception as e:
            st.error(f"Error durante el preprocesamiento: {e}")



# Carga de dataframes y preprocesamiento de datos
cargar_preprocesar_datos_iniciales()


# MENU LATERAL
with st.sidebar:
    opcion_seleccionada = option_menu(
        menu_title="Plai Padel Pro",
        options=["Formulario", "Recomendador de Pala", "Graficas de palas","Graficas de Formularios"], 
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