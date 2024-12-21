import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import seaborn as sns

#Import archivos de utilidas : utilidades y tratamiento_de_datos_formulario
from utilidades.utilidades import  descargar_generar_archivo_palas_s3
from utilidades.tratamiento_de_datos.tratamiento_de_datos_formulario import procesar_datos_formulario_csv,crear_dataframes_con_scores,procesar_scores_y_guardar
from utilidades.tratamiento_de_datos.tratamiento_de_datos_palas import lectura_tratamiento_datos_palas, labelizar_columnas, calcular_scores, escalar_columnas, generar_graficos

#Algoritmo importado(KNN)
from utilidades.utilidades import encontrar_vecinos_mas_cercanos_knn

#Diccionarios Importados
from utilidades.utilidades import OPCIONES_SELECTBOX_FORMULARIO
from utilidades.utilidades import LABEL_MAPPING_TIPO_DE_JUEGO
from utilidades.utilidades import PRECIO_MAXIMO_MAP
from utilidades.utilidades import LABEL_MAPPING

# Configuración de la página para ancho completo
st.set_page_config(page_title="Formulario", layout="wide")

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
    df_form = pd.read_json('df_scaled_formularios.csv', lines=True)
    df_palas = pd.read_csv('df_scaled_palas.csv')
    
    # Verificar si 'Score_Escalar' existe, si no, calcularlo como placeholder (ejemplo)
    if 'Score_Escalar' not in df_form.columns:
        df_form['Score_Escalar'] = 0.5  # Placeholder o cálculo inicial
    
    if 'Score_Escalar' not in df_palas.columns:
        df_palas['Score_Escalar'] = df_palas['score_nivel'] * 0.5 + df_palas['score_lesion'] * 0.5
    
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

# Función para calcular Score y Score_Escalar
def calcular_score(sum_features_keys):
    # Sumar los valores seleccionados en el formulario para calcular el Score
    score = sum_features_keys
    
    # Calcular Score_Escalar basado en un máximo posible (7 en este caso)
    score_escalar = score / max(7, score) if score else None
    
    return score, score_escalar


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
# Mostrar detalles del registro seleccionado en forma tabular sin Score
def mostrar_detalles_registro_tabular(df_form, index):
    selected_row = df_form.iloc[index]
    return pd.DataFrame({"Característica": selected_row.drop(["Score_Escalar_Lesion", "Score_Escalar_Nivel"]).index, 
                         "Valor": selected_row.drop(["Score_Escalar_Lesion", "Score_Escalar_Nivel"]).values})

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

# Función para analizar la relación entre Score y palas recomendadas
def analizar_relacion_score(df_palas):
    st.subheader("Pala Recomendada Evitar Lesión (Tipo de Juego)")
    
    # Mapear los valores numéricos de "Tipo de Juego" a etiquetas descriptivas
    if "Tipo de Juego" in df_palas.columns:
        df_palas["Tipo de Juego Descriptivo"] = df_palas["Tipo de Juego"].map(LABEL_MAPPING_TIPO_DE_JUEGO)
    else:
        st.error("La columna 'Tipo de Juego' no existe en el DataFrame.")
        return
    
    # Verificar si hay datos en df_palas
    if df_palas.empty:
        st.error("El DataFrame 'df_palas' está vacío.")
        return
    
    # Crear checkboxes para seleccionar qué tipos de juego mostrar
    categorias_unicas = df_palas["Tipo de Juego Descriptivo"].unique()
    
    col1, col2, col3, col4 = st.columns(len(categorias_unicas))
    seleccionados = {}
    
    for i, categoria in enumerate(categorias_unicas):
        with [col1, col2, col3, col4][i]:
            seleccionados[categoria] = st.checkbox(categoria, value=(categoria == "Polivalente"))
    
    categorias_seleccionadas = [categoria for categoria, mostrar in seleccionados.items() if mostrar]
    df_filtrado = df_palas[df_palas["Tipo de Juego Descriptivo"].isin(categorias_seleccionadas)]
    
    if df_filtrado.empty:
        st.warning("No hay datos para las categorías seleccionadas.")
        return
    
    # Crear gráfico interactivo en 2D con plotly (scatter plot)
    fig = px.scatter(
        df_filtrado,
        x="score_lesion",
        y="score_nivel",
        color="Tipo de Juego Descriptivo",
        size="Score_Escalar",
        hover_data=["Palas", "Precio", "Balance"],
        title="Pala Recomendada Evitar Lesión (Tipo de Juego)"
    )
    
    # Ajustar diseño del gráfico
    fig.update_layout(
        xaxis_title="Lesión (%)",
        yaxis_title="Nivel (%)",
        margin=dict(l=40, r=40, t=40, b=40),  # Márgenes ajustados
        height=600  # Altura del gráfico
    )
    
    st.plotly_chart(fig)

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

# Función para el formulario
def formulario():
    # Título del Formulario
    st.title("Formulario")
    
    col1, col2, col3 = st.columns(3)

    # Configuración de los selectboxes usando las opciones centralizadas
    with col1:
        peso_key = st.selectbox("Indica tu peso (kg)", list(OPCIONES_SELECTBOX_FORMULARIO["opciones_peso"].keys()))
        altura_key = st.selectbox("Indica tu altura (cm)", list(OPCIONES_SELECTBOX_FORMULARIO["opciones_altura"].keys()))
        sexo_key = st.selectbox("Indica tu sexo", list(OPCIONES_SELECTBOX_FORMULARIO["opciones_sexo"].keys()))
        rango_precios_key = st.selectbox("¿Cuánto dinero estás dispuesto a pagar por una pala?", list(OPCIONES_SELECTBOX_FORMULARIO["opciones_rango_precio"].keys()))
        horas_semana_key = st.selectbox("¿Cuántas horas juega a la semana?", list(OPCIONES_SELECTBOX_FORMULARIO["opciones_horas_semana"].keys()))

    with col2:
        nivel_de_juego_key = st.selectbox("¿Cuál es tu Nivel de juego?", list(OPCIONES_SELECTBOX_FORMULARIO["opciones_nivel_de_juego"].keys()))
        tipo_de_juego_key = st.selectbox("¿Qué tipo de Juego te gusta?", list(OPCIONES_SELECTBOX_FORMULARIO["opciones_tipo_de_juego"].keys()))
        tipo_de_balance_key_option = st.selectbox("¿Qué tipo de Balance te gusta?", list(OPCIONES_SELECTBOX_FORMULARIO["opciones_balance"].keys()))
        lado_de_juego_key = st.selectbox("Indique su lado de juego", list(OPCIONES_SELECTBOX_FORMULARIO["opciones_rango_juego"].keys()))

    with col3:
        lesiones_antiguas_key = st.selectbox("¿Has tenido alguna lesión previamente?", list(OPCIONES_SELECTBOX_FORMULARIO["opciones_lesiones_antiguas"].keys()))
        frecuencia_lesion_key = st.selectbox("¿Cuándo sueles caer lesionado?", list(OPCIONES_SELECTBOX_FORMULARIO["opciones_frecuencia_lesion"].keys()))
        cuanto_lesion_key = st.selectbox("¿Cuánto tiempo pasó desde tu última lesión?", list(OPCIONES_SELECTBOX_FORMULARIO["opciones_cuanto_lesion"].keys()))

    # Botón para enviar el formulario
    enviar_btn_clicked = st.button("Enviar")

    if enviar_btn_clicked:
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

        """ # Calcular los valores correspondientes a las claves seleccionadas
        sum_keys = (
            OPCIONES_SELECTBOX_FORMULARIO["opciones_peso"][peso_key] +
            OPCIONES_SELECTBOX_FORMULARIO["opciones_altura"][altura_key] +
            OPCIONES_SELECTBOX_FORMULARIO["opciones_sexo"][sexo_key] +
            OPCIONES_SELECTBOX_FORMULARIO["opciones_rango_precio"][rango_precios_key] +
            OPCIONES_SELECTBOX_FORMULARIO["opciones_horas_semana"][horas_semana_key] +
            OPCIONES_SELECTBOX_FORMULARIO["opciones_nivel_de_juego"][nivel_de_juego_key] +
            OPCIONES_SELECTBOX_FORMULARIO["opciones_tipo_de_juego"][tipo_de_juego_key] +
            OPCIONES_SELECTBOX_FORMULARIO["opciones_balance"][tipo_de_balance_key_option] +
            OPCIONES_SELECTBOX_FORMULARIO["opciones_rango_juego"][lado_de_juego_key] +
            OPCIONES_SELECTBOX_FORMULARIO["opciones_lesiones_antiguas"][lesiones_antiguas_key] +
            OPCIONES_SELECTBOX_FORMULARIO["opciones_frecuencia_lesion"][frecuencia_lesion_key] +
            OPCIONES_SELECTBOX_FORMULARIO["opciones_cuanto_lesion"][cuanto_lesion_key]
        ) """

        nuevo_registro['Score_Escalar_Lesion']
        nuevo_registro['Score_Escalar_Nivel'] 

        # Actualizar el DataFrame con el nuevo registro
        df_form_actualizado = obtener_dataframe_actualizado()
        df_form_actualizado = pd.concat([df_form_actualizado, pd.DataFrame([nuevo_registro])], ignore_index=True)

        # Reordenar las columnas para que Score y Score_Escalar estén al final
        columnas = list(df_form_actualizado.columns)
        columnas.remove('Score')
        columnas.remove('Score_Escalar')
        columnas.extend(['Score', 'Score_Escalar'])
        df_form_actualizado = df_form_actualizado[columnas]

        # Guardar el DataFrame actualizado en session_state
        guardar_dataframe_actualizado(df_form_actualizado)

        # Mostrar éxito y el último registro agregado
        st.success("Formulario enviado correctamente.")
        st.write("Nuevo registro agregado:")
        ultimo_registro = df_form_actualizado.iloc[[-1]]
        st.dataframe(ultimo_registro)


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
        
        # Mostrar detalles del registro seleccionado en forma tabular
        detalles_registro_df = mostrar_detalles_registro_tabular(df_form, index)
        
        st.subheader("Detalles del Registro Seleccionado")
        st.dataframe(detalles_registro_df)

        # Obtener valores del registro seleccionado en el formulario
        score_escalar = df_form.iloc[index]['Score_Escalar']
        
        # Checkbox para considerar el precio
        considerar_precio = st.checkbox("Considerar Precio Dispuesto A Pagar")
        
        # Determinar el rango de precio máximo según la selección del usuario
        rango_precio_seleccionado = detalles_registro_df.loc[
            detalles_registro_df["Característica"] == "Rango de precio dispuesto a pagar", 
            "Valor"
        ].values[0]
        

        # Verificar si el valor está en el mapa antes de usarlo
        if rango_precio_seleccionado in PRECIO_MAXIMO_MAP:
           precio_maximo = PRECIO_MAXIMO_MAP[rango_precio_seleccionado]
        else:
           st.error(f"Rango de precio '{rango_precio_seleccionado}' no reconocido.")
           return
        
        # Encontrar vecinos más cercanos con KNN (palas recomendadas)
        x_random = df_palas['score_lesion'].mean()
        y_random = df_palas['score_nivel'].mean()
        
        palas_recomendadas_df = encontrar_vecinos_mas_cercanos_knn(
            df_palas,
            x_random=x_random,
            y_random=y_random,
            z_random=score_escalar,
            considerar_precio=considerar_precio,
            precio_maximo=precio_maximo
        )
        
        st.subheader("Palas Recomendadas")
        st.dataframe(palas_recomendadas_df)

        graficar_distribucion_caracteristicas(palas_recomendadas_df)

        # Graficar el gráfico de calor
        graficar_calor_caracteristicas(palas_recomendadas_df)

        # Llamar a la función para analizar la relación entre Score y palas recomendadas
        analizar_relacion_score(df_palas)

    except Exception as e:
       st.error(f"Error al generar el gráfico o procesar los datos: {str(e)}")

st.write("1.DESCARGA DE DATA - FORMULARIO y PALAS")
st.write("Descargando datos desde S3...")
try:
    descargar_generar_archivo_palas_s3()
except Exception as e:
    st.error(f"Error al descargar o generar archivos desde S3: {e}")
    st.stop()

st.write("2.PRE-PROCESAMIENTO DE DATOS DEL FORMULARIO")

st.write("Aplicando Label Encoding - CSV Formulario")
try:
    procesar_datos_formulario_csv()
except Exception as e:
    st.error(f"Error al procesar datos del formulario: {e}")
    st.stop()

st.write("Generando DataFrames con Scores...")
try:
    crear_dataframes_con_scores()
except Exception as e:
    st.error(f"Error al crear DataFrames con scores: {e}")
    st.stop()

st.write("Procesando Scores y guardando resultados...")
try:
    procesar_scores_y_guardar()
except Exception as e:
    st.error(f"Error al procesar scores o guardar resultados: {e}")

st.write("3.PRE-PROCESAMIENTO DE DATOS DE PALAS")
st.write("Carga/Lectura/Tratamiento de Datos de Palas")
try:
    lectura_tratamiento_datos_palas()
except Exception as e:
    st.error(f"Error en la lectura del tratamiento de palas {e}")
    st.stop()
st.write("Labelizar Columnas de Palas")
try:
    labelizar_columnas()
except Exception as e:
    st.error(f"Error al labelizar las columnas del dataframe de palas {e}")
    st.stop()
st.write("Calcular scores de lesion y nivel de Palas")
try:
    calcular_scores()
except Exception as e:
    st.error(f"Error al labelizar las columnas del dataframe de palas {e}")
    st.stop()
st.write("Escalar Columnas de Palas")
try:
    escalar_columnas()
except Exception as e:
    st.error(f"Error al escalar columnas del dataframe de palas {e}")
    st.stop()


# Menú lateral moderno con streamlit-option-menu
with st.sidebar:
   opcion_seleccionada = option_menu(
       menu_title="Plai Padel Pro",
       options=["Formulario", "Recomendador de Pala"],
       icons=["pencil-fill", "bar-chart-fill"],
       menu_icon="cast",
       default_index=0,
)

# Mostrar la opción seleccionada
if opcion_seleccionada == "Formulario":
   formulario()
elif opcion_seleccionada == "Recomendador de Pala":
   recomendador_de_pala()