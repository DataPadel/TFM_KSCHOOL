import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import seaborn as sns

# Configuración de la página para ancho completo
st.set_page_config(page_title="Formulario", layout="wide")


"""
APP STREAMLIT V2 (INCORPORACION DE REGISTROS - ULTIMA VERSION - CUIDADO CON MODIFICAR)

COMO VISUALIZAR STREAMLIT EN LOCAL

- Instalacion de la librerias en Visual Studio Code necesarias mediante pip
  
  pip install streamlit
  pip install streamlit-option-menu

- Levantar en local el servidor con la aplicacion de Streamlit (Terminal de Visual Studio Code)

    <Ruta_Local_De_Cada_Persona>\TFM_KSCHOOL\Raul\Trabajando_Con_Cositas_Luis> streamlit run <nombre_archivo_version>.py 

   streamlit run <nombre_archivo_version>.py
   Ejemplo --- streamlit run app_streamlit_V2.py
  

CAMBIOS EN LA VERSION

  Funmcionando

- Se pueden introducir los registros mediante el formulario. Utilizas los desplegables y le das a enviar
  Se mostrara debajo una tabla con el registro ingresado. Si cambias a la ventana a Recomendador de Pala
  y vas a la barra de seleccionar el indice de Registro vas a ver que ha cambiado el numerito y ha subido
  una unidad. LOS REGISTROS SON EN CACHE, CADA VEZ QUE LEVANTAMOS LA APLICACION LOS REGISTROS SE BORRAN

  Otros Cambios

- Son pruebas mediante archivos .csv ya cargados de como implantar un KNN y graficos. Estos estan sujetos
  a modificaciones
  
"""

# Diccionario de mapeo para convertir valores numéricos a etiquetas descriptivas
LABEL_MAPPING = {
    "Balance": {0: "No data", 1: "Bajo", 2: "Medio", 3: "Alto"},
    "Dureza": {0: "No data", 1: "Blanda", 2: "Media", 3: "Dura"},
    "Nivel de Juego": {0: "No Data", 1: "Iniciacion", 2: "Intermedio", 3: "Avanzado"},
    "Forma": {0: "No Data", 1: "Redonda", 2: "Lágrima", 3: "Diamante"},
    "Tipo de Juego": {0: "No Data", 1: "Control", 2: "Polivalente", 3: "Potencia"}
}



# Función para cargar y validar los DataFrames
@st.cache_data
def cargar_dataframes():
    df_form = pd.read_json('dataframe_final_formulario.json', lines=True)
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
    return pd.DataFrame({"Característica": selected_row.drop(["Score", "Score_Escalar"]).index, 
                         "Valor": selected_row.drop(["Score", "Score_Escalar"]).values})

# Encontrar vecinos más cercanos con KNN considerando el precio si está seleccionado
def encontrar_vecinos_mas_cercanos_knn(df_palas, x_random, y_random, z_random, considerar_precio, precio_maximo):
    knn_features = ['score_lesion', 'score_nivel', 'Score_Escalar']
    
    if considerar_precio:
        knn_features.append('Precio')
        df_palas = df_palas[df_palas['Precio'] <= precio_maximo]
    
    knn = NearestNeighbors(n_neighbors=3)
    knn.fit(df_palas[knn_features])
    
    reference_point = [[x_random, y_random, z_random] + ([precio_maximo] if considerar_precio else [])]
    
    distances, indices = knn.kneighbors(reference_point)
    
    palas_recomendadas = df_palas.iloc[indices[0]]
    
    # Mapear valores numéricos a etiquetas descriptivas
    palas_recomendadas["Nivel de Juego"] = palas_recomendadas["Nivel de Juego"].map(LABEL_MAPPING["Nivel de Juego"])
    palas_recomendadas["Tipo de Juego"] = palas_recomendadas["Tipo de Juego"].map(LABEL_MAPPING["Tipo de Juego"])
    palas_recomendadas["Balance"] = palas_recomendadas["Balance"].map(LABEL_MAPPING["Balance"])
    
    return palas_recomendadas[['Palas', 'Nivel de Juego', 'Tipo de Juego', 'Balance', 'Precio']]

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

# Diccionario de mapeo para convertir valores numéricos a etiquetas descriptivas
LABEL_MAPPING_TIPO_DE_JUEGO = {0: "No Related", 1: "Control", 2: "Polivalente", 3: "Potencia"}

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
    
    # Opciones de los distintos desplegables de los inputs
    opciones_peso = {"Entre 51 y 70 Kg": 0, "Entre 71 y 90 Kg": 0, "Más de 91 Kg": 0.5}
    opciones_altura = {"Entre 1,51 y 1,70 metros": 0, "Entre 1,71 y 1,80 metros": 0, "Mas de 1,80 metros": 0.5}
    opciones_nivel_de_juego = {"Iniciacion": 0, "Intermedio": 1, "Avanzado": 2}
    opciones_tipo_de_juego = {"Ofensivo": 1, "Defensivo": 0}
    opciones_balance = {"Medio": 0, "Alto": 0.5}
    opciones_horas_semana = {"Menos de 3,5 horas": 0, "Mas de 3.5 horas": 0.5}
    opciones_rango_precio = {"Menos de 100": 0, "Entre 100 y 200": 0, "Mas de 200": 0}
    opciones_rango_juego = {"Drive": 0, "Reves": 0.5}
    opciones_lesiones_antiguas = {
        "Lumbares": 0.5,
        "Epicondilitis": 0.15,
        "Gemelos o fascitis": 0.5,
        "Cervicales": 0.25,
        "Hombros": 0.5,
        "Ninguna": 0
    }
    opciones_frecuencia_lesion = {
        "Siempre que juego defensivamente": 0.5,
        "Siempre que juego ofensivamente": 0.5,
        "Casi siempre que juego intensamente": 0.25,
        "Rara vez cuando juego": 0.15
    }
    opciones_cuanto_lesion = {
        "Menos de 3 meses": 0.5,
        "Entre 3 y 6 meses": 0.25,
        "Mas de 6 meses": 0.15
    }

    col1, col2, col3 = st.columns(3)

    with col1:
        # Peso
        peso_key = st.selectbox("Indica tu peso (kg)", list(opciones_peso.keys()))
        peso_value_option = opciones_peso[peso_key]

        # Altura
        altura_key = st.selectbox("Indica tu altura (cm)", list(opciones_altura.keys()))
        altura_value_option = opciones_altura[altura_key]

        # Rango de precios
        rango_precios_key = st.selectbox("¿Cuánto dinero estás dispuesto a pagar por una pala?", list(opciones_rango_precio.keys()))
        rango_precios_value_option = opciones_rango_precio[rango_precios_key]

        # Horas por semana
        horas_semana_key = st.selectbox("¿Cuántas horas juega a la semana?", list(opciones_horas_semana.keys()))
        horas_semana_value_option = opciones_horas_semana[horas_semana_key]

    with col2:
        # Nivel de juego
        nivel_de_juego_key = st.selectbox("¿Cuál es tu Nivel de juego?", list(opciones_nivel_de_juego.keys()))
        nivel_de_juego_value_option = opciones_nivel_de_juego[nivel_de_juego_key]

        # Tipo de juego
        tipo_de_juego_key = st.selectbox("¿Qué tipo de Juego te gusta?", list(opciones_tipo_de_juego.keys()))
        tipo_de_juego_value_option = opciones_tipo_de_juego[tipo_de_juego_key]

        # Tipo de balance
        tipo_de_balance_key_option = st.selectbox("¿Qué tipo de Balance te gusta?", list(opciones_balance.keys()))
        tipo_de_balance_value_option = opciones_balance[tipo_de_balance_key_option]

        # Lado de juego
        lado_de_juego_key = st.selectbox("Indique su lado de juego", list(opciones_rango_juego.keys()))
        lado_de_juego_value_option = opciones_rango_juego[lado_de_juego_key]

    with col3:
        # Lesiones antiguas
        lesiones_antiguas_key = st.selectbox("¿Has tenido alguna lesión previamente?", list(opciones_lesiones_antiguas.keys()))
        lesiones_antiguas_value_option = opciones_lesiones_antiguas[lesiones_antiguas_key]

        # Frecuencia lesión
        frecuencia_lesion_key = st.selectbox("¿Cuándo sueles caer lesionado?", list(opciones_frecuencia_lesion.keys()))
        frecuencia_lesion_value_option = opciones_frecuencia_lesion[frecuencia_lesion_key]

        # Cuánto tiempo desde la última lesión
        cuanto_lesion_key = st.selectbox("¿Cuánto tiempo pasó desde tu última lesión?", list(opciones_cuanto_lesion.keys()))
        cuanto_lesion_value_option = opciones_cuanto_lesion[cuanto_lesion_key]

    # Botón para enviar el formulario
    enviar_btn_clicked = st.button("Enviar")

    if enviar_btn_clicked:
        nuevo_registro= {
            'Cuantas horas juega a la semana': horas_semana_key,
            'Indique su peso': peso_key,
            'Indique su altura': altura_key,
            'Rango de precio dispuesto a pagar': rango_precios_key,
            'Indique su lado de juego': lado_de_juego_key,
            'Indique su nivel de juego': nivel_de_juego_key,
            'Tipo de juego': tipo_de_juego_key,
            'Que tipo de balance te gusta': tipo_de_balance_key_option,
            'Has tenido alguna de las siguientes lesiones previamente lumbares, epicondilitis, gemelos, fascitis, cervicales u hombros': lesiones_antiguas_key,
            'Con que frecuencia': frecuencia_lesion_key,
            'Hace cuanto': cuanto_lesion_key
        }


        sum_keys= (
            peso_value_option + altura_value_option + rango_precios_value_option +
            horas_semana_value_option + nivel_de_juego_value_option +
            tipo_de_juego_value_option + tipo_de_balance_value_option +
            lado_de_juego_value_option + lesiones_antiguas_value_option +
            frecuencia_lesion_value_option + cuanto_lesion_value_option
        )

        nuevo_registro['Score'] = sum_keys
        nuevo_registro['Score_Escalar'] = (sum_keys * 7) / 100

        
          # Crear un DataFrame temporal con el nuevo registro
        df_form_actualizado = obtener_dataframe_actualizado()
        df_form_actualizado = pd.concat([df_form_actualizado, pd.DataFrame([nuevo_registro])], ignore_index=True)

        # Reordenar las columnas para que Score y Score_Escalar estén al final
        columnas = list(df_form_actualizado.columns)
        columnas.remove('Score')
        columnas.remove('Score_Escalar')
        columnas.extend(['Score', 'Score_Escalar'])  # Añadirlas al final
        df_form_actualizado = df_form_actualizado[columnas]

        # Guardar el DataFrame actualizado
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
        
        precio_maximo_map = {
            "Menos de 100": 100,
            "Entre 100 y 200 ": 200,
            "Mas de 200 ": float('inf')
        }

        # Verificar si el valor está en el mapa antes de usarlo
        if rango_precio_seleccionado in precio_maximo_map:
           precio_maximo = precio_maximo_map[rango_precio_seleccionado]
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