import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import seaborn as sns

#Import archivos de utilidades : utilidades y tratamiento_de_datos_formulario
from utilidades.utilidades import  descargar_generar_archivo_palas_s3
from utilidades.tratamiento_de_datos.tratamiento_de_datos_formulario import procesar_datos_formulario_csv,crear_dataframes_con_scores,procesar_scores_y_guardar,regresion_a_la_media_formulario
from utilidades.tratamiento_de_datos.tratamiento_de_datos_palas import lectura_tratamiento_datos_palas, labelizar_columnas, calcular_scores, escalar_columnas, regresion_a_la_media_palas,ejecutar_una_vez

#Import graficas de Palas
from utilidades.graficos.graficos_palas import grafico_histograma_palas, diagrama_dispersion_palas,diagrama_3d_palas

#Importar graficas de Formularios
from utilidades.graficos.graficos_formularios import grafico_dispersion_formularios

#Importar fraficos de Recomendador de Pala
from utilidades.graficos.graficos_recomendador_de_pala import diagrama_palas_palas_recomendadas,diagrama_palas_palas_recomendadas_grafica

#Algoritmo importado(KNN) y Visualizador de Gráficos
from utilidades.utilidades import encontrar_vecinos_mas_cercanos_knn,analizar_relacion_score

#Diccionarios Importados
from utilidades.utilidades import OPCIONES_SELECTBOX_FORMULARIO
from utilidades.utilidades import LABEL_MAPPING_TIPO_DE_JUEGO
from utilidades.utilidades import LABEL_MAPPING

# Configuración de la página para ancho completo
st.set_page_config(page_title="Formulario", layout="wide")

# Inicializar el estado global para controlar la navegación
if "menu_option" not in st.session_state:
    st.session_state["menu_option"] = "Formulario"

if "datos_procesados" not in st.session_state:
    st.session_state["datos_procesados"] = False  # Indica si los datos ya fueron procesados


# Función para manejar el preprocesamiento inicial

def preprocesar_datos_iniciales():
    """Preprocesa los datos iniciales solo una vez."""
    if not st.session_state.get("datos_procesados", False):
        try:
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

# Llamar a la función de preprocesamiento inicial solo una vez
preprocesar_datos_iniciales()
"""
APP STREAMLIT V4 (!!!APLICACION NO OPERATIVA!!!!)(IN PROGRESS)

COMO VISUALIZAR STREAMLIT EN LOCAL

- Instalacion de la librerias en Visual Studio Code necesarias mediante pip
  
  pip install streamlit
  pip install streamlit-option-menu

- Levantar en local el servidor con la aplicacion de Streamlit (Terminal de Visual Studio Code)

    <Ruta_Local_De_Cada_Persona>\TFM_KSCHOOL\Raul\Trabajando_Con_Cositas_Luis> streamlit run <nombre_archivo_version>.py 

   streamlit run <nombre_archivo_version>.py
   Ejemplo --- streamlit run app_streamlit_V2.py
  

CAMBIOS EN LA VERSION
TAREA 1
- Todo lo implementado por Luis en este Jupiter Notebook (luis_json-caracteristicas-ponderadas) se ejecuta ya
   sobre la aplicacion automaticamente al cargarse. Esto implica los siguientes puntos

  - Descarga de ficheros JSON de S3 (HECHO)
  - Generacion de Dataframes/CSVs a partir de JSON descargados de S3 tanto Formulario como Palas(Hecho)
  - Label Encoding aplicado a columnas categóricas en Formulario(Hecho)
  - Generados df_scored_lesion y df_scored_nivel (Hecho)
  - Generacion de archivo 'df_scaled_formularios.csc' con escalares de lesion y nivel

TODO TAREA2
   - Implementar estas ponderaciones nuevas sobre streamlit(IN PROGRESS)

TODO TAREA3
    - Introducir nueva selectbox de sexo en el formulario(IN PROGRESS)

TODO TAREA4
    - Hacer que todo sea funcional
    
PARA CERRAR LA TERMINAL DE STREAMLIT CTRL + C | CTRL + Z

"""

# Función para cargar y validar los DataFrames
@st.cache_data
def cargar_dataframes():
    df_form = pd.read_csv('df_scaled_formularios_3.0.csv')
    df_palas = pd.read_csv('df_scaled_palas_3.0.csv')
    return df_form, df_palas


# Función para guardar el DataFrame actualizado en el estado global
def guardar_dataframe_actualizado(df_form):
    st.session_state["df_form"] = df_form

# Función para obtener el DataFrame actualizado desde el estado global
def obtener_dataframe_actualizado():
    if "df_form" in st.session_state:
        return st.session_state["df_form"]
    else:
        df_form, _ = cargar_dataframes()
        st.session_state["df_form"] = df_form  # Asegurar que se guarde en session_state
        return df_form

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
        

# Renombrar columnas del DataFrame df_form
def renombrar_columnas(df_form):
    column_mapping = {
        "Cuantas horas juegas a la semana": "Horas a la Semana",
        "Indique su peso": "Peso",
        "Indique su sexo":"Sexo",
        "Indique su altura": "Altura",
        "Indique su Lado de Juego": "Lado de Juego",
        "Indique su nivel de juego": "Nivel de Juego",
        "Que tipo de balance te gusta": "Balance",
        "Has tenido alguna de las siguientes lesiones ...": "Lesiones Antiguas",
        "Con que frecuencia": "Frecuencia Lesion",
        "Hace cuanto": "Tiempo entre Lesiones"
    }
    df_form.rename(columns=column_mapping, inplace=True)
    return df_form
    #return df_form.drop(columns=["Score", "Score_Escalar", "Rango de precio dispuesto a pagar"], errors='ignore')

# Mostrar detalles del registro seleccionado en forma tabular
def mostrar_detalles_registro_tabular(df_form, index):
    """
    Muestra los detalles de un registro en formato tabular, excluyendo columnas no deseadas.

    Args:
        df_form (pd.DataFrame): DataFrame que contiene los registros.
        index (int): Índice del registro a mostrar.

    Returns:
        pd.DataFrame: DataFrame con las características y valores del registro seleccionado.
    """
    # Identificar columnas no deseadas
    columnas_no_deseadas = [
        "Score_Escalar_Lesion", "Score_Escalar_Nivel",
        "Score_Escalar_Ajustado_Lesion", "Score_Escalar_Ajustado_Nivel"
    ]

    # Filtrar las columnas no deseadas y eliminar duplicados
    selected_row = df_form.drop(columns=columnas_no_deseadas, errors='ignore').iloc[index]

    # Filtrar valores None o NaN
    selected_row = selected_row.dropna()

    # Crear el DataFrame de detalles
    return pd.DataFrame({
        "Característica": selected_row.index,
        "Valor": selected_row.values
    })


# Función para crear un gráfico de calor
def graficar_calor_caracteristicas(palas_recomendadas):

    st.subheader("Gráfico de Calor - Características Palas Recomendadas")

    # Convertir las columnas categóricas en valores numéricos para calcular la correlación
    mapeo_inverso = {v: k for k, v in LABEL_MAPPING["Nivel de Juego"].items()}
    palas_recomendadas['Nivel de Juego Numérico'] = palas_recomendadas['Nivel de Juego'].map(mapeo_inverso)
    
    mapeo_inverso_tipo_juego = {v: k for k, v in LABEL_MAPPING["Tipo de Juego"].items()}
    palas_recomendadas['Tipo de Juego Numérico'] = palas_recomendadas['Tipo de Juego'].map(mapeo_inverso_tipo_juego)
    
    mapeo_inverso_balance = {v: k for k, v in LABEL_MAPPING["Balance"].items()}
    palas_recomendadas['Balance Numérico'] = palas_recomendadas['Balance'].map(mapeo_inverso_balance)
    
    # Seleccionar solo las columnas numéricas relevantes
    datos_numericos = palas_recomendadas[['Nivel de Juego Numérico', 'Tipo de Juego Numérico', 'Balance Numérico', 'Precio']]
    
    # Calcular la matriz de correlación
    matriz_correlacion = datos_numericos.corr()
    
    # Crear el gráfico de calor usando seaborn
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(matriz_correlacion, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    
    st.pyplot(fig)


# Grafico - Pala Recomendada Evitar Lesión (Tipo de Juego)

def graficar_distribucion_caracteristicas(palas_recomendadas):
    fig_barra = px.bar(
        palas_recomendadas.melt(id_vars='Palas', value_vars=['Nivel de Juego', 'Tipo de Juego', 'Balance']),
        x='variable',
        y='value',
        color='Palas',
        barmode='group',
        title='Distribución por Características'
    )
    
    st.plotly_chart(fig_barra)

# CSS personalizado para eliminar márgenes y ajustar espaciado

custom_css = """

<style>
/* Centrar todo el contenido y limitar su ancho al 80% */
[data-testid="stAppViewContainer"] {
    max-width: 70%; /* Ancho máximo del contenido */
    margin: 0 auto; /* Centrar horizontalmente */
    padding-top: 1rem; /* Espaciado superior */
    padding-bottom: 1rem; /* Espaciado inferior */
}

/* Ajustar márgenes entre columnas */
.css-1kyxreq {
    padding-left: 0rem;
    padding-right: 0rem;
}

/* Centrar el botón de enviar */
button[kind="primary"] {
    margin-top: 1rem;
    display: block;
    margin-left: auto;
    margin-right: auto;
}

/* Ajustar márgenes de los expanders */
[data-testid="stExpander"] {
    margin-top: 1rem;
    margin-bottom: 1rem;
}
</style>
"""

# Aplicar CSS personalizado
st.markdown(custom_css, unsafe_allow_html=True)

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

    # Función para marcar que el formulario ha sido modificado
    def actualizar_estado_formulario():
        st.session_state["formulario_modificado"] = True
        st.session_state["formulario_enviado"] = False  # Reinicia el estado de enviado

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
            list(OPCIONES_SELECTBOX_FORMULARIO["opciones_rango_precio"].keys()),
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
            list(OPCIONES_SELECTBOX_FORMULARIO["opciones_balance"].keys()),
            key="tipo_de_balance_key_option",
            on_change=actualizar_estado_formulario,
        )
        lado_de_juego_key = st.selectbox(
            "Indique su lado de juego",
            list(OPCIONES_SELECTBOX_FORMULARIO["opciones_rango_juego"].keys()),
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


def recomendador_de_pala():
    st.title("Recomendador de Pala")

    try:
        # Obtener el DataFrame actualizado desde el estado global
        df_form = obtener_dataframe_actualizado()
        _, df_palas = cargar_dataframes()

        # Renombrar columnas del DataFrame formulario
        df_form = renombrar_columnas(df_form)

        # Slider para seleccionar índice del registro en el formulario
        index = st.slider("Índice del Registro Formulario", min_value=0, max_value=len(df_form) - 1, step=1)

        # Validar índice seleccionado
        if index < 0 or index >= len(df_form):
            st.error("El índice seleccionado está fuera de rango.")
            return

        # Crear nueva columna 'Score_Escalar_Lesion_Nivel' basada en la intersección geométrica
        df_form['Score_Escalar_Lesion_Nivel'] = (
            (df_form['Score_Escalar_Lesion']**2 + df_form['Score_Escalar_Nivel']**2)**0.5
        )

        # Mostrar detalles del registro seleccionado en forma tabular
        st.subheader("Detalles del Registro Seleccionado")
        detalles_registro_df = mostrar_detalles_registro_tabular(df_form, index)
        st.dataframe(detalles_registro_df)

        # Obtener el valor de "Rango de precio dispuesto a pagar" del registro seleccionado
        rango_precio_seleccionado = detalles_registro_df.loc[
            detalles_registro_df["Característica"] == "Rango de precio dispuesto a pagar", 
            "Valor"
        ].values[0].strip()  # Eliminar espacios adicionales

        # Depuración: Imprimir el rango seleccionado
        print(f"Rango de precio seleccionado: '{rango_precio_seleccionado}'")

        # Determinar los rangos seleccionados automáticamente según el valor del formulario
        rangos_seleccionados = []
        if rango_precio_seleccionado == "Menos de 100":
            rangos_seleccionados.append((0, 100))
        elif rango_precio_seleccionado == "Entre 100 y 200":
            rangos_seleccionados.append((100, 200))
        elif rango_precio_seleccionado == "Mas de 200":
            rangos_seleccionados.append((200, float('inf')))

        if not rangos_seleccionados:
            st.warning("Por favor, selecciona al menos un rango de precios.")
            return

        # Obtener valores específicos del registro seleccionado
        x_random = df_form.iloc[index]['Score_Escalar_Lesion']
        y_random = df_form.iloc[index]['Score_Escalar_Nivel']

        # Iterar sobre los rangos seleccionados y generar recomendaciones por cada rango
        for rango in rangos_seleccionados:
            precio_maximo = rango[1]  # Máximo del rango actual

            try:
                # Llamar al método encontrar_vecinos_mas_cercanos_knn para cada rango
                palas_recomendadas = encontrar_vecinos_mas_cercanos_knn(
                    df_palas=df_palas,
                    x_random=x_random,
                    y_random=y_random,
                    considerar_precio=True,
                    precio_maximo=precio_maximo
                )

                if not palas_recomendadas.empty:
                    st.subheader(f"Palas Recomendadas para el rango {rango[0]} - {rango[1]} Euros")
                    st.dataframe(palas_recomendadas)
                    
                    # Mostrar gráfico relacionado con las recomendaciones
                    diagrama_palas_palas_recomendadas(palas_recomendadas)
                    
                    diagrama_palas_palas_recomendadas_grafica(palas_recomendadas)

            except ValueError as knn_error:
                if "No hay suficientes palas" in str(knn_error):
                    st.warning(f"No hay suficientes palas disponibles en el rango {rango[0]} - {rango[1]} Euros.")
                else:
                    raise knn_error

    except Exception as e:
       st.error(f"Error al generar el gráfico o procesar los datos: {str(e)}")


def graficas_palas():
    st.title("Graficas de Palas")

    try:
        grafico_histograma_palas()
        diagrama_dispersion_palas()
        diagrama_3d_palas()
    except Exception as e:
       st.error(f"Error al generar el gráfico o procesar los datos: {str(e)}")
       
def graficas_formularios():
    st.title("Graficas de Formularios")

    try:
        grafico_dispersion_formularios()
        
    except Exception as e:
       st.error(f"Error al generar el gráfico o procesar los datos: {str(e)}")

# Menú lateral incluyendo la opción "Graficas de palas"
with st.sidebar:
    opcion_seleccionada = option_menu(
        menu_title="Plai Padel Pro",
        options=["Formulario", "Recomendador de Pala", "Graficas de palas","Graficas de Formularios"], 
        icons=["pencil-fill", "bar-chart-fill", "graph-up","graph-up"], 
        menu_icon="cast",
        default_index=0,
        key="menu_option"
    )

# Condiciones para manejar las diferentes opciones del menú
if st.session_state["menu_option"] == "Formulario":
    formulario()
elif st.session_state["menu_option"] == "Recomendador de Pala":
    recomendador_de_pala()
elif st.session_state["menu_option"] == "Graficas de palas": 
    graficas_palas()
elif st.session_state["menu_option"] == "Graficas de Formularios": 
    graficas_formularios()