import base64
import pandas as pd
import seaborn as sns
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu

#Importar utilidades App - Importar funciones utilizadas en el fichero principal de la app
from utilidades.app.utilidadaes_app import cargar_dataframes, obtener_dataframe_actualizado,actualizar_estado_formulario,analizador_graficos_datos,clasificador_golpes_padel

#Importar archivos de utilidades : utilidades y tratamiento_de_datos_formulario
from utilidades.utilidades import  descargar_generar_archivo_palas_s3
from utilidades.tratamiento_de_datos.tratamiento_de_datos_formulario import procesar_datos_formulario_csv,crear_dataframes_con_scores,procesar_scores_y_guardar,regresion_a_la_media_formulario
from utilidades.tratamiento_de_datos.tratamiento_de_datos_palas import lectura_tratamiento_datos_palas, labelizar_columnas, calcular_scores, escalar_columnas, regresion_a_la_media_palas,ejecutar_una_vez

#Importar Recomendador de Palas

from utilidades.app.recomendador_de_palas import recomendador_de_palas
#Import graficas de Palas
from utilidades.graficos.graficos_palas import graficas_palas

#Importar graficas de Formularios
from utilidades.graficos.graficos_formularios import graficas_formularios

#Algoritmo importado(KNN) y Visualizador de Gráficos
from utilidades.utilidades import encontrar_vecinos_mas_cercanos_knn,analizar_relacion_score

#Diccionarios Importados
from utilidades.utilidades import OPCIONES_SELECTBOX_FORMULARIO

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


# Función para guardar el DataFrame actualizado en el estado global
def guardar_dataframe_actualizado(df_form):
    st.session_state["df_form"] = df_form


def agregar_registro(df_actual, nuevo_registro):
    """
    Agrega un nuevo registro al DataFrame existente asegurando índices únicos y consistencia en las columnas.

    Args:
        df_actual (pd.DataFrame): El DataFrame actual.
        nuevo_registro (dict): El nuevo registro a agregar.

    Returns:
        pd.DataFrame: El DataFrame actualizado con el nuevo registro.
    """
    # Convertir el nuevo registro en un DataFrame
    nuevo_df = pd.DataFrame([nuevo_registro])

    # Verificar si alguno de los DataFrames tiene índices duplicados y reiniciar los índices si es necesario
    if not df_actual.index.is_unique:
        print("El DataFrame actual tiene índices duplicados. Se reiniciarán los índices.")
        df_actual = df_actual.reset_index(drop=True)

    if not nuevo_df.index.is_unique:
        print("El nuevo registro tiene índices duplicados. Se reiniciarán los índices.")
        nuevo_df = nuevo_df.reset_index(drop=True)

    # Asegurar que las columnas sean consistentes entre ambos DataFrames
    columnas_faltantes = set(df_actual.columns) - set(nuevo_df.columns)
    for col in columnas_faltantes:
        nuevo_df[col] = None  # Agregar columnas faltantes al nuevo registro con valores nulos

    columnas_faltantes_en_actual = set(nuevo_df.columns) - set(df_actual.columns)
    for col in columnas_faltantes_en_actual:
        df_actual[col] = None  # Agregar columnas faltantes al DataFrame actual con valores nulos

    # Concatenar asegurando que los índices sean únicos
    return pd.concat([df_actual, nuevo_df], ignore_index=True)



def guardar_csv(df, csv_file_path):
    """
    Guarda un DataFrame en un archivo CSV después de verificar y normalizar las columnas.
    
    Args:
        df (pd.DataFrame): El DataFrame a guardar.
        csv_file_path (str): La ruta del archivo CSV.
    """
    try:
        # Eliminar columnas duplicadas
        df = df.loc[:, ~df.columns.duplicated()]

        # Definir el orden estricto de las columnas
        columnas_deseadas = [
            'Cuantas horas juega a la semana',
            'Indique su peso',
            'Indique su altura',
            'Indique su sexo',
            'Rango de precio dispuesto a pagar',
            'Indique su lado de juego',
            'Indique su nivel de juego',
            'Tipo de juego',
            'Que tipo de balance te gusta',
            'Has tenido alguna de las siguientes lesiones previamente lumbares, epicondilitis, gemelos, fascitis, cervicales u hombros',
            'Con que frecuencia',
            'Hace cuanto'
        ]

        # Asegurarse de que solo estén las columnas deseadas
        df = df[columnas_deseadas]

        # Guardar el archivo CSV
        df.to_csv(csv_file_path, index=False)
        print("Archivo guardado correctamente.")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")
        

def formulario():
    """
    Genera un formulario interactivo en Streamlit para recopilar datos del usuario,
    actualiza el DataFrame en `st.session_state` y procesa los datos al enviarse.
    """
    # Título del Formulario
    st.title("Formulario")

    # Inicializar estados en session_state
    if "formulario_enviado" not in st.session_state:
        st.session_state["formulario_enviado"] = False
    if "formulario_modificado" not in st.session_state:
        st.session_state["formulario_modificado"] = False

    # Crear columnas para los selectboxes
    col1, col2, col3 = st.columns(3)

    # Configuración de los selectboxes usando las opciones centralizadas
    with col1:
        peso_key = st.selectbox(
            "Indica tu peso (kg)",
            list(OPCIONES_SELECTBOX_FORMULARIO["opciones_peso"].keys()),
            key="peso_key",
            on_change=actualizar_estado_formulario,
        )
        altura_key = st.selectbox(
            "Indica tu altura (cm)",
            list(OPCIONES_SELECTBOX_FORMULARIO["opciones_altura"].keys()),
            key="altura_key",
            on_change=actualizar_estado_formulario,
        )
        sexo_key = st.selectbox(
            "Indica tu sexo",
            list(OPCIONES_SELECTBOX_FORMULARIO["opciones_sexo"].keys()),
            key="sexo_key",
            on_change=actualizar_estado_formulario,
        )
        rango_precios_key = st.selectbox(
            "¿Cuánto dinero estás dispuesto a pagar por una pala?",
            list(OPCIONES_SELECTBOX_FORMULARIO["opciones_rango_precios"].keys()),
            key="rango_precios_key",
            on_change=actualizar_estado_formulario,
        )
        horas_semana_key = st.selectbox(
            "¿Cuántas horas juega a la semana?",
            list(OPCIONES_SELECTBOX_FORMULARIO["opciones_horas_semana"].keys()),
            key="horas_semana_key",
            on_change=actualizar_estado_formulario,
        )

    with col2:
        nivel_de_juego_key = st.selectbox(
            "¿Cuál es tu Nivel de juego?",
            list(OPCIONES_SELECTBOX_FORMULARIO["opciones_nivel_de_juego"].keys()),
            key="nivel_de_juego_key",
            on_change=actualizar_estado_formulario,
        )
        tipo_de_juego_key = st.selectbox(
            "¿Qué tipo de Juego te gusta?",
            list(OPCIONES_SELECTBOX_FORMULARIO["opciones_tipo_de_juego"].keys()),
            key="tipo_de_juego_key",
            on_change=actualizar_estado_formulario,
        )
        tipo_de_balance_key_option = st.selectbox(
            "¿Qué tipo de Balance te gusta?",
            list(OPCIONES_SELECTBOX_FORMULARIO["opciones_tipo_de_balance"].keys()),
            key="tipo_de_balance_key_option",
            on_change=actualizar_estado_formulario,
        )
        lado_de_juego_key = st.selectbox(
            "Indique su lado de juego",
            list(OPCIONES_SELECTBOX_FORMULARIO["opciones_lado_de_juego"].keys()),
            key="lado_de_juego_key",
            on_change=actualizar_estado_formulario,
        )

    with col3:
        lesiones_antiguas_key = st.selectbox(
            "¿Has tenido alguna lesión previamente?",
            list(OPCIONES_SELECTBOX_FORMULARIO["opciones_lesiones_antiguas"].keys()),
            key="lesiones_antiguas_key",
            on_change=actualizar_estado_formulario,
        )
        frecuencia_lesion_key = st.selectbox(
            "¿Cuándo sueles caer lesionado?",
            list(OPCIONES_SELECTBOX_FORMULARIO["opciones_frecuencia_lesion"].keys()),
            key="frecuencia_lesion_key",
            on_change=actualizar_estado_formulario,
        )
        cuanto_lesion_key = st.selectbox(
            "¿Cuánto tiempo pasó desde tu última lesión?",
            list(OPCIONES_SELECTBOX_FORMULARIO["opciones_cuanto_lesion"].keys()),
            key="cuanto_lesion_key",
            on_change=actualizar_estado_formulario,
        )

    # Botón para enviar el formulario
    enviar_btn_clicked = st.button("Enviar")

    if enviar_btn_clicked:
        # Marcar que el formulario ha sido enviado y no modificado
        st.session_state.formulario_enviado = True
        st.session_state.formulario_modificado = False

        # Crear un nuevo registro con las claves seleccionadas
        nuevo_registro = {
            'Cuantas horas juega a la semana': horas_semana_key,
            'Indique su peso': peso_key,
            'Indique su altura': altura_key,
            'Indique su sexo': sexo_key,
            'Rango de precio dispuesto a pagar': rango_precios_key,
            'Indique su lado de juego': lado_de_juego_key,
            'Indique su nivel de juego': nivel_de_juego_key,
            'Tipo de juego': tipo_de_juego_key,
            'Que tipo de balance te gusta': tipo_de_balance_key_option,
            'Has tenido alguna de las siguientes lesiones previamente lumbares, epicondilitis, gemelos, fascitis, cervicales u hombros': lesiones_antiguas_key,
            'Con que frecuencia': frecuencia_lesion_key,
            'Hace cuanto': cuanto_lesion_key
        }

        # Actualizar el DataFrame y guardar en session_state
        df_form_actualizado = obtener_dataframe_actualizado()
        df_form_actualizado = agregar_registro(df_form_actualizado, nuevo_registro)
        guardar_dataframe_actualizado(df_form_actualizado)

        # Guardar los cambios en el archivo CSV
        guardar_csv(df_form_actualizado, 'formulario_combinaciones.csv')

    # Ejecutar funciones solo si el formulario ha sido enviado y no modificado
    if st.session_state.formulario_enviado and not st.session_state.formulario_modificado:
        procesar_datos_formulario_csv()  # Aplicar LabelEncoder
        crear_dataframes_con_scores()
        procesar_scores_y_guardar()
        regresion_a_la_media_formulario()

    if enviar_btn_clicked:
        # Mostrar éxito en Streamlit después del envío
        st.success("Formulario enviado correctamente.")


def actualizar_estado_formulario():
    """
    Marca que el formulario ha sido modificado cuando se cambia alguna opción.
    """
    st.session_state.formulario_modificado = True


def procesar_envio_formulario():
    """
    Procesa el envío del formulario y actualiza los datos.
    """
    nuevo_registro = {
        'Cuantas horas juega a la semana': st.session_state.horas_semana_key,
        'Indique su peso': st.session_state.peso_key,
        'Indique su altura': st.session_state.altura_key,
        'Indique su sexo': st.session_state.sexo_key,
        'Rango de precio dispuesto a pagar': st.session_state.rango_precios_key,
        'Indique su lado de juego': st.session_state.lado_de_juego_key,
        'Indique su nivel de juego': st.session_state.nivel_de_juego_key,
        'Tipo de juego': st.session_state.tipo_de_juego_key,
        'Que tipo de balance te gusta': st.session_state.tipo_de_balance_key_option,
        'Has tenido alguna de las siguientes lesiones previamente lumbares, epicondilitis, gemelos, fascitis, cervicales u hombros': st.session_state.lesiones_antiguas_key,
        'Con que frecuencia': st.session_state.frecuencia_lesion_key,
        'Hace cuanto': st.session_state.cuanto_lesion_key
    }

    
    # Mostrar el nuevo registro en la interfaz
    st.subheader("Nuevo Registro")
    st.write(nuevo_registro)  # Muestra el registro como una tabla
    # Actualizar el DataFrame y guardar en session_state
    df_form_actualizado = obtener_dataframe_actualizado()
    df_form_actualizado = agregar_registro(df_form_actualizado, nuevo_registro)
    guardar_dataframe_actualizado(df_form_actualizado)

    # Guardar los cambios en el archivo CSV
    guardar_csv(df_form_actualizado, 'formulario_combinaciones.csv')


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